<script lang="ts">
import { onMount } from 'svelte';
import { page } from '$app/stores';
import { splitsService } from '$lib/services/api';
import { receiptStore, splitStore, currencyStore, templatesStore, groupsStore } from '$lib/stores';
import { calculateSplit } from '$lib/services/offline';
import { offlineStore } from '$lib/stores/offline';

  import PersonManager from '$lib/components/features/split/PersonManager.svelte';
  import SplitResults from '$lib/components/features/split/SplitResults.svelte';
  import CurrencySelector from '$lib/components/CurrencySelector.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let people = $state<string[]>(['Person 1', 'Person 2']);
  let tax = $state(0);
  let tip = $state(0);
  let calculating = $state(false);
  let loading = $state(false);
  let selectedTemplate = $state<any>(null);
  let selectedGroup = $state<any>(null);
  let quickTip = $state<number | null>(null);
  let autoDetectTax = $state(true);
  let roundingMode = $state<'exact' | 'up' | 'down'>('exact');
  let splitMethod = $state<'equal' | 'percentage'>('equal');

  // Quick tip percentages
  const quickTipOptions = [
    { label: '10%', value: 0.10 },
    { label: '15%', value: 0.15 },
    { label: '18%', value: 0.18 },
    { label: '20%', value: 0.20 },
    { label: '25%', value: 0.25 }
  ];

  onMount(async () => {
    await Promise.all([
      currencyStore.init(),
      templatesStore.loadTemplates(),
      groupsStore.loadGroups()
    ]);

    // Check for template or group in URL
    const url = new URL(window.location.href);
    const templateId = url.searchParams.get('template');
    const groupId = url.searchParams.get('group');
    const receiptId = url.searchParams.get('receiptId');

    if (templateId) {
      const template = $templatesStore.templates.find(t => t.id === templateId);
      if (template) {
        selectedTemplate = template;
        people = [...template.people];
        tax = template.tax || 0;
        tip = template.tip || 0;
      }
    }

    if (groupId) {
      const group = $groupsStore.groups.find(g => g.id === groupId);
      if (group) {
        selectedGroup = group;
        people = [...group.members];
      }
    }

    // Load receipt data if available
    if (receiptId) {
      try {
        const response = await splitsService.getReceipt(receiptId);
        if (response.parsed_data) {
          receiptStore.setData(response.parsed_data);
          // Auto-detect tax if enabled
          if (autoDetectTax && response.parsed_data.tax) {
            tax = response.parsed_data.tax;
          }
        }
      } catch (error) {
        console.error('Failed to load receipt:', error);
      }
    }
  });

  function handleQuickTip(percentage: number) {
    quickTip = percentage;
    const subtotal = $receiptStore.data?.items.reduce((sum, item) => sum + item.price, 0) || 0;
    tip = subtotal * percentage;
  }

  async function handleCalculateSplit() {
    calculating = true;
    loading = true;
    const receiptData = $receiptStore.data;

    if (!receiptData || !receiptData.items.length) {
      alert('Please upload a receipt first');
      calculating = false;
      loading = false;
      return;
    }

    // Create assignments (each item assigned to all people by default)
    const assignments = receiptData.items.map((item: any) => ({
      item_id: item.name,
      assigned_to: people,
    }));

    const request = {
      person_names: people,
      item_assignments: assignments,
      tax_amount_input: tax,
      tip_amount_input: tip,
      split_evenly: false,
    };

    if ($offlineStore.online) {
      // Online: Use API
      splitsService.calculate(request)
        .then(async response => {
          splitStore.setResults(response.split_results);
          splitStore.setPeople(people);
          splitStore.setItems(receiptData.items);

          // Save to IndexedDB for history
          try {
            const { getIndexedDB, STORES } = await import('$lib/services/offline/indexeddb');
            const indexedDB = await getIndexedDB();
            await indexedDB.add(STORES.SPLITS, {
              id: response.split_id,
              results: response.split_results,
              createdAt: Date.now()
            });
          } catch (saveError) {
            console.error('Failed to save split to history:', saveError);
          }
        })
        .catch(error => {
          alert(`Failed to calculate split: ${error.message}`);
        })
        .finally(() => {
          calculating = false;
          loading = false;
        });
    } else {
      // Offline: Use client-side calculation
      try {
        const result = calculateSplit(people, receiptData.items, assignments, tax, tip, false);

        // Store result
        splitStore.setResults(result);
        splitStore.setPeople(people);
        splitStore.setItems(receiptData.items);

        // Save to IndexedDB for history (with a temporary ID)
        try {
          const { getIndexedDB, STORES } = await import('$lib/services/offline/indexeddb');
          const indexedDB = await getIndexedDB();
          const tempId = 'offline-' + Date.now();
          await indexedDB.add(STORES.SPLITS, {
            id: tempId,
            results: result,
            createdAt: Date.now()
          });
        } catch (saveError) {
          console.error('Failed to save offline split to history:', saveError);
        }
      } catch (error) {
        alert(`Failed to calculate split: ${error instanceof Error ? error.message : String(error)}`);
      } finally {
        calculating = false;
        loading = false;
      }
    }
  }

  function resetSplit() {
    people = ['Person 1', 'Person 2'];
    tax = 0;
    tip = 0;
    splitStore.reset();
  }
</script>

<svelte:head>
  <title>Create Split - Split Bill</title>
</svelte:head>

<div class="space-y-4">
  <!-- Person Manager -->
  <PersonManager people={people} onUpdate={(p) => people = p} />

  <!-- Currency Selector -->
  <div class="flex justify-end">
    <CurrencySelector />
  </div>

  <!-- Template/Group Info -->
  {#if selectedTemplate || selectedGroup}
    <Card>
      <div class="flex items-center justify-between">
        <div>
          {#if selectedTemplate}
            <p class="text-sm text-text-secondary">Using template: <span class="font-semibold">{selectedTemplate.name}</span></p>
          {/if}
          {#if selectedGroup}
            <p class="text-sm text-text-secondary">Group: <span class="font-semibold">{selectedGroup.name}</span></p>
          {/if}
        </div>
        <Button variant="ghost" size="sm" onclick={() => { selectedTemplate = null; selectedGroup = null; }}>Change</Button>
      </div>
    </Card>
  {/if}

   <!-- Tax & Tip -->
  <Card>
    <div class="space-y-4">
      <!-- Tax & Split Method -->
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="font-semibold">Tax</h2>
          <label class="flex items-center gap-2 text-sm">
            <input type="checkbox" bind:checked={autoDetectTax} />
            Auto-detect tax
          </label>
        </div>
        <!-- Split Method Tabs -->
        <div class="flex items-center gap-2">
          <button
            class={splitMethod === 'equal' ? 'px-4 py-2 bg-brand-50 border border-brand-500 rounded-lg text-brand-700 font-semibold' : 'px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg'}
            onclick={() => splitMethod = 'equal'}
          >
            Equal Split
          </button>
          <button
            class={splitMethod === 'percentage' ? 'px-4 py-2 bg-brand-50 border border-brand-500 rounded-lg text-brand-700 font-semibold' : 'px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg'}
            onclick={() => splitMethod = 'percentage'}
          >
            % Split
          </button>
        </div>
      </div>

      <div>
        <label for="tax-input" class="block text-sm font-medium mb-1">Tax</label>
        <input
          id="tax-input"
          type="number"
          bind:value={tax}
          step="0.01"
          min="0"
          class="w-full px-4 py-3 text-base bg-white border border-surface-300 rounded-lg min-h-[44px]"
          placeholder="0.00"
          disabled={autoDetectTax}
        />
      </div>

      <div>
        <label for="tip-input" class="block text-sm font-medium mb-1">Tip</label>
        <div class="space-y-3">
          <input
            id="tip-input"
            type="number"
            bind:value={tip}
            step="0.01"
            min="0"
            class="w-full px-4 py-3 text-base bg-white border border-surface-300 rounded-lg min-h-[44px]"
            placeholder="0.00"
            {#if splitMethod === 'percentage'}
              disabled={quickTip !== null}
            {/if}
          />

          <!-- Smart Rounding (only when not percentage split) -->
          {#if splitMethod === 'equal'}
            <div class="mt-3">
              <p class="text-sm text-text-secondary mb-2">Smart Rounding</p>
              <div class="grid grid-cols-3 gap-2">
                <button
                  class={roundingMode === 'down' ? 'px-3 py-2 bg-brand-50 border border-brand-500 rounded-lg text-brand-700 font-semibold' : 'px-3 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg'}
                  onclick={() => roundingMode = 'down'}
                >
                  Down
                </button>
                <button
                  class={roundingMode === 'exact' ? 'px-3 py-2 bg-brand-50 border border-brand-500 rounded-lg text-brand-700 font-semibold' : 'px-3 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg'}
                  onclick={() => roundingMode = 'exact'}
                >
                  Exact
                </button>
                <button
                  class={roundingMode === 'up' ? 'px-3 py-2 bg-brand-50 border border-brand-500 rounded-lg text-brand-700 font-semibold' : 'px-3 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg'}
                  onclick={() => roundingMode = 'up'}
                >
                  Up
                </button>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </Card>

  <!-- Actions -->
  <div class="flex gap-2">
    <Button
      variant="primary"
      onclick={handleCalculateSplit}
      disabled={calculating}
      class="flex-1"
    >
      {calculating ? 'Calculating...' : 'Calculate Split'}
    </Button>
    <Button
      variant="ghost"
      onclick={resetSplit}
      disabled={calculating}
    >
      Reset
    </Button>
  </div>

  <!-- Results -->
  {#if $splitStore.results}
    <SplitResults results={$splitStore.results} />
  {/if}
</div>
