<script lang="ts">
  import { splitsService } from '$lib/services/api';
  import { receiptStore } from '$lib/stores/receipt';
  import PersonManager from '$lib/components/features/split/PersonManager.svelte';
  import SplitResults from '$lib/components/features/split/SplitResults.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Progress from '$lib/components/ui/Progress.svelte';
  import type { ReceiptData } from '$lib/types/receipt';

  let people = $state<string[]>(['Person 1', 'Person 2']);
  let tax = $state(0);
  let tip = $state(0);
  let calculating = $state(false);

  function handleCalculateSplit() {
    calculating = true;
    const receiptData = receiptStore.data;

    if (!receiptData || !receiptData.items.length) {
      alert('Please upload a receipt first');
      calculating = false;
      return;
    }

    // Create assignments (each item assigned to all people by default)
    const assignments = receiptData.items.map(item => ({
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

    splitsService.calculate(request)
      .then(response => {
        receiptStore.setResults?.(response.split_results);
      })
      .catch(error => {
        alert(`Failed to calculate split: ${error.message}`);
      })
      .finally(() => {
        calculating = false;
      });
  }

  function resetSplit() {
    people = ['Person 1', 'Person 2'];
    tax = 0;
    tip = 0;
    receiptStore.reset?.();
  }
</script>

<svelte:head>
  <title>Create Split - Split Bill</title>
</svelte:head>

<div class="space-y-4">
  <!-- Person Manager -->
  <PersonManager people={people} onUpdate={(p) => people = p} />

  <!-- Tax & Tip -->
  <Card>
    <div class="space-y-4">
      <h2 class="font-semibold">Tax & Tip</h2>

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
        />
      </div>

      <div>
        <label for="tip-input" class="block text-sm font-medium mb-1">Tip</label>
        <input
          id="tip-input"
          type="number"
          bind:value={tip}
          step="0.01"
          min="0"
          class="w-full px-4 py-3 text-base bg-white border border-surface-300 rounded-lg min-h-[44px]"
          placeholder="0.00"
        />
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
  {#if receiptStore.results}
    <SplitResults results={receiptStore.results} />
  {/if}
</div>
