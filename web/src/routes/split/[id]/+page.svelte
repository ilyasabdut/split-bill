<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import SettlementGraph from '$lib/components/SettlementGraph.svelte';
  import PaymentBadge from '$lib/components/PaymentBadge.svelte';
  import QRCodeShare from '$lib/components/QRCodeShare.svelte';
  import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';
  import { splitsService, paymentsService } from '$lib/services/api';
  import { currencyStore } from '$lib/stores/currency';
  import type { SplitResults } from '$lib/types/split';

  let splitData = $state<{
    results: SplitResults;
    createdAt: number;
    people: string[];
    total: number;
    payments?: any[];
  } | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let showQRCode = $state(false);
  let paymentStatus = $state<Record<string, 'pending' | 'paid' | 'partial'>>({});

  const splitId = $derived($page.params.id);

  onMount(async () => {
    try {
      await currencyStore.init();

      // First try to get from server
      const response = await splitsService.getShared(splitId);

      // Load payment status
      try {
        const payments = await paymentsService.getPaymentsBySplit(splitId);
        const status: Record<string, 'pending' | 'paid' | 'partial'> = {};
        payments.forEach(payment => {
          status[payment.payee_id] = payment.status;
        });
        paymentStatus = status;
      } catch (paymentErr) {
        console.error('Failed to load payments:', paymentErr);
      }

      splitData = {
        results: response.split_results,
        createdAt: new Date(response.created_at).getTime(),
        people: Object.keys(response.split_results),
        total: Object.values(response.split_results).reduce((sum: number, person: any) => sum + person.total, 0)
      };
    } catch (err) {
      // If server fails, try local storage
      try {
        const indexedDB = await getIndexedDB();
        const localData = await indexedDB.get<any>(STORES.SPLITS, splitId);

        if (localData) {
          splitData = {
            results: localData.results,
            createdAt: localData.createdAt,
            people: Object.keys(localData.results),
            total: Object.values(localData.results).reduce((sum: number, person: any) => sum + person.total, 0)
          };
        } else {
          error = 'Split not found';
        }
      } catch (localErr) {
        error = 'Failed to load split data';
      }
    } finally {
      loading = false;
    }
  });

  async function markAsPaid(personName: string) {
    try {
      await paymentsService.createPayment({
        split_id: splitId,
        payer_id: 'current_user', // This would come from auth
        payee_id: personName,
        amount: splitData.results[personName].total,
        status: 'paid'
      });
      paymentStatus[personName] = 'paid';
      paymentStatus = { ...paymentStatus };
    } catch (err) {
      alert('Failed to record payment');
    }
  }

  function formatDate(timestamp: number): string {
    return new Date(timestamp).toLocaleString();
  }

  async function copyShareLink() {
    await navigator.clipboard.writeText(window.location.href);
    alert('Link copied to clipboard!');
  }

  function shareSplit() {
    if (navigator.share) {
      navigator.share({
        title: 'Split Bill',
        text: `Check out this bill split: ${splitData?.people.join(', ')}`,
        url: window.location.href
      });
    } else {
      copyShareLink();
    }
  }
</script>

<svelte:head>
  <title>Split Details - Split Bill</title>
</svelte:head>

{#if loading}
  <Card>
    <div class="text-center py-8">
      <p class="text-text-secondary">Loading split details...</p>
    </div>
  </Card>
{:else if error}
  <Card>
    <div class="text-center py-8">
      <div class="text-5xl mb-4" aria-hidden="true">❌</div>
      <h3 class="font-semibold mb-2">Error</h3>
      <p class="text-text-secondary mb-4">{error}</p>
      <Button onclick={() => window.history.back()}>Go Back</Button>
    </div>
  </Card>
{:else if splitData}
  <div class="space-y-4">
    <Card>
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">Split Details</h2>
          <p class="text-sm text-text-secondary">{formatDate(splitData.createdAt)}</p>
        </div>

        <div class="text-center p-4 bg-primary-50 rounded-lg">
          <p class="text-sm text-primary-700">Total Amount</p>
          <p class="text-3xl font-bold text-primary-700">
            {currencyStore.formatCurrency(splitData.total)}
          </p>
        </div>

        <!-- Settlement Graph -->
        <SettlementGraph results={splitData.results} />

        <!-- Per-Person Breakdown -->
        <div class="space-y-3">
          {#each Object.entries(splitData.results) as [name, data]}
            <div class="p-4 bg-surface-50 rounded-lg">
              <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-3">
                  <h3 class="font-semibold">{name}</h3>
                  <PaymentBadge status={paymentStatus[name] || 'pending'} />
                </div>
                <span class="text-lg font-bold">{currencyStore.formatCurrency(data.total)}</span>
              </div>
              <p class="text-sm text-text-secondary mb-3">
                {data.items.length} items • Tax: {currencyStore.formatCurrency(data.tax_share)} • Tip: {currencyStore.formatCurrency(data.tip_share)}
              </p>

              <!-- Payment Button -->
              {#if paymentStatus[name] !== 'paid'}
                <Button
                  variant="outline"
                  size="sm"
                  onclick={() => markAsPaid(name)}
                >
                  Mark as Paid
                </Button>
              {/if}

              {#if data.items.length > 0}
                <details class="mt-3">
                  <summary class="text-sm text-text-secondary cursor-pointer">View items</summary>
                  <ul class="mt-2 space-y-1">
                    {#each data.items as item}
                      <li class="text-sm flex justify-between">
                        <span>{item.name} {item.quantity > 1 ? `×${item.quantity}` : ''}</span>
                        <span>{currencyStore.formatCurrency(item.price)}</span>
                      </li>
                    {/each}
                  </ul>
                </details>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    </Card>

    <!-- QR Code Sharing -->
    <Card>
      <h3 class="font-semibold mb-3">Share this Split</h3>
      <QRCodeShare
        url={window.location.href}
        title="Split Bill"
        description={`Split with ${splitData.people.join(', ')}`}
      />
    </Card>

    <!-- Share Actions -->
    <div class="flex gap-2">
      <Button variant="primary" onclick={shareSplit} class="flex-1">
        📢 Share
      </Button>
      <Button variant="secondary" onclick={copyShareLink}>
        📎 Copy Link
      </Button>
    </div>
  </div>
{/if}
