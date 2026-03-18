<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import SettlementGraph from '$lib/components/SettlementGraph.svelte';
  import PaymentBadge from '$lib/components/PaymentBadge.svelte';
  import QRCodeShare from '$lib/components/QRCodeShare.svelte';
  import ActivityFeedItem from '$lib/components/ActivityFeedItem.svelte';
  import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';
  import { splitsService, paymentsService } from '$lib/services/api';
  import { currencyStore } from '$lib/stores/currency';
  import type { SplitResults } from '$lib/types/split';
  import type { Activity } from '$lib/components/ActivityFeedItem.svelte';

  let splitData = $state<{
    results: SplitResults;
    createdAt: number;
    people: string[];
    total: number;
    receiptData?: any;
    payments?: any[];
  } | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let showQRCode = $state(false);
  let paymentStatus = $state<Record<string, 'pending' | 'paid' | 'partial'>>({});
  let activityFeed = $state<Activity[]>([]);

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

      // Calculate total
      const total = Object.values(response.split_results).reduce((sum: number, person: any) => sum + person.total, 0);

      splitData = {
        results: response.split_results,
        createdAt: new Date(response.created_at).getTime(),
        people: Object.keys(response.split_results),
        total,
        receiptData: response.receipt_data
      };

      // Generate mock activity feed
      generateActivityFeed();
    } catch (err) {
      // If server fails, try local storage
      try {
        const indexedDB = await getIndexedDB();
        const localData = await indexedDB.get<any>(STORES.SPLITS, splitId);

        if (localData) {
          const total = Object.values(localData.results).reduce((sum: number, person: any) => sum + person.total, 0);
          splitData = {
            results: localData.results,
            createdAt: localData.createdAt,
            people: Object.keys(localData.results),
            total,
            receiptData: localData.receipt_data
          };
          generateActivityFeed();
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

  function generateActivityFeed() {
    // Generate mock activity feed data
    activityFeed = [
      {
        id: '1',
        type: 'split_created',
        user: { id: 1, name: 'You' },
        data: { split_name: splitData?.people.join(', ') || 'Bill Split' },
        created_at: new Date(splitData?.createdAt || Date.now()).toISOString()
      },
      {
        id: '2',
        type: 'payment_made',
        user: { id: 2, name: splitData?.people[0] || 'Someone' },
        data: { amount: currencyStore.formatCurrency(splitData?.results?.[splitData?.people[0]]?.total || 0), currency: 'USD' },
        created_at: new Date((splitData?.createdAt || Date.now()) + 3600000).toISOString()
      },
      {
        id: '3',
        type: 'split_completed',
        user: { id: 1, name: 'You' },
        data: { split_name: splitData?.people.join(', ') || 'Bill Split' },
        created_at: new Date((splitData?.createdAt || Date.now()) + 7200000).toISOString()
      }
    ];
  }

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

      // Add to activity feed
      activityFeed = [
        {
          id: Date.now().toString(),
          type: 'payment_made',
          user: { id: 1, name: 'You' },
          data: { amount: currencyStore.formatCurrency(splitData.results[personName].total), currency: 'USD' },
          created_at: new Date().toISOString()
        },
        ...activityFeed
      ];
    } catch (err) {
      alert('Failed to record payment');
    }
  }

  function formatDate(timestamp: number): string {
    return new Date(timestamp).toLocaleString();
  }

  function formatRelativeTime(timestamp: number): string {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return new Date(timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  async function copyShareLink() {
    await navigator.clipboard.writeText(window.location.href);
    alert('Link copied to clipboard!');
  }

  function goHome() {
    goto('/');
  }

  function createNewSplit() {
    goto('/split');
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

  function getPersonInitials(name: string): string {
    return name.charAt(0).toUpperCase();
  }

  function getPersonColor(name: string): string {
    const colors = [
      'bg-brand-100 text-brand-700',
      'bg-violet-100 text-violet-700',
      'bg-amber-100 text-amber-700',
      'bg-rose-100 text-rose-700',
      'bg-emerald-100 text-emerald-700',
      'bg-blue-100 text-blue-700'
    ];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  }

  function getFoodIcon(itemName: string): string {
    const icons: Record<string, string> = {
      salmon: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-orange-600"><path d="M2 12h20"/><path d="M12 2v20"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10-4.5-10-10-10Z"/></svg>`,
      roll: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-orange-600"><path d="M2 12h20"/><path d="M12 2v20"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10-4.5-10-10-10Z"/></svg>`,
      miso: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-600"><path d="M4 6h16"/><path d="M4 6v4c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V6"/><path d="M6 12h12"/><path d="M6 12v4c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-4"/></svg>`,
      soup: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-600"><path d="M4 6h16"/><path d="M4 6v4c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V6"/><path d="M6 12h12"/><path d="M6 12v4c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-4"/></svg>`,
      default: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-orange-600"><path d="M2 12h20"/><path d="M12 2v20"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10-4.5-10-10-10Z"/></svg>`
    };

    const lowerName = itemName.toLowerCase();
    if (lowerName.includes('salmon') || lowerName.includes('roll')) return icons.salmon;
    if (lowerName.includes('miso') || lowerName.includes('soup')) return icons.miso;
    return icons.default;
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
  <div class="space-y-6 px-4 pt-14 pb-24">
    <!-- Header -->
    <div class="flex items-start justify-between gap-3">
      <a href="/" class="shrink-0 inline-flex items-center justify-center w-11 h-11 rounded-xl bg-surface-0 shadow-md border border-surface-200 active:scale-[0.99]">
        <svg class="w-6 h-6 text-text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        <span class="sr-only">Back</span>
      </a>

      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-brand-100 text-brand-700">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </span>
          <p class="text-xs font-semibold text-brand-700">Split Detail</p>
        </div>
        <h1 class="mt-1 text-lg font-semibold leading-tight truncate">Dinner at Nori House</h1>
      </div>

      <button type="button" class="shrink-0 inline-flex items-center justify-center w-11 h-11 rounded-xl bg-surface-0 shadow-md border border-surface-200 active:scale-[0.99]" aria-label="More actions">
        <svg class="w-6 h-6 text-text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
        </svg>
      </button>
    </div>

    <!-- Amount summary card -->
    <Card class="shadow-md">
      <div class="flex items-start justify-between gap-4 p-4">
        <div class="min-w-0">
          <p class="text-xs font-medium text-text-secondary">Total bill</p>
          <div class="mt-1 flex items-baseline gap-1">
            <p class="text-3xl font-semibold tracking-tight">{$currencyStore.formatCurrency(splitData.total)}</p>
            <span class="text-sm font-medium text-text-tertiary">USD</span>
          </div>
          <p class="text-xs text-text-tertiary font-medium">≈ €{($currencyStore.formatCurrency(splitData.total) as string).replace('$', '')} EUR</p>

          <div class="mt-3 flex flex-wrap items-center gap-2">
            <span class="inline-flex items-center gap-1.5 rounded-full bg-brand-50 text-brand-700 px-3 py-1 text-xs font-semibold border border-brand-100">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              {splitData.people.length} people
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-full bg-surface-50 text-text-primary px-3 py-1 text-xs font-semibold border border-surface-200">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Tip included
            </span>
          </div>
        </div>
        <div class="shrink-0">
          <div class="w-14 h-14 rounded-2xl bg-brand-500 text-white shadow-md flex items-center justify-center">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </div>
    </Card>

    <!-- Settlement Overview -->
    <section>
      <h2 class="text-sm font-semibold text-text-primary mb-3 px-1">Settlement</h2>
      <Card class="shadow-md">
        <div class="p-4 grid gap-4">
          {#each Object.entries(splitData.results) as [name, data]}
            {#if name !== 'Ava (You)'}
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class={`w-8 h-8 rounded-full ${getPersonColor(name)} flex items-center justify-center text-xs font-bold`}>
                    {getPersonInitials(name)}
                  </div>
                  <div class="flex flex-col">
                    <span class="text-sm font-medium text-text-primary">{name} owes you</span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold text-text-primary">{$currencyStore.formatCurrency(data.total)}</span>
                  <svg class="w-4 h-4 text-text-tertiary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </div>
              </div>
            {/if}
          {/each}
        </div>
        <div class="bg-surface-50 px-4 py-2 border-t border-surface-200 text-center">
           <p class="text-xs text-text-secondary">Total receivable: <span class="font-semibold text-text-primary">$42.30</span></p>
        </div>
      </Card>
    </section>

    <!-- Settlement Graph -->
    <section>
      <h2 class="text-sm font-semibold text-text-primary mb-3 px-1">Settlement Graph</h2>
      <Card class="shadow-md">
        <div class="p-4">
          <SettlementGraph results={splitData.results} />
        </div>
      </Card>
    </section>

    <!-- Receipt & Items -->
    <section class="grid gap-4">
      <!-- Itemized Breakdown -->
      <div>
         <h2 class="text-sm font-semibold text-text-primary mb-3 px-1">Items</h2>
         <Card class="shadow-md">
            <div class="divide-y divide-slate-100">
              {#each Object.entries(splitData.results) as [name, data]}
               {#each data.items as item, index}
                   {#if index < 2}
                     <div class="p-3 flex items-center justify-between">
                       <div class="flex items-center gap-3">
                         <span class="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center">
                           {@html getFoodIcon(item.name)}
                         </span>
                         <div>
                           <p class="text-sm font-medium text-text-primary">{item.name}</p>
                           <p class="text-xs text-text-secondary">{name}</p>
                         </div>
                       </div>
                       <span class="text-sm font-semibold text-text-primary">{$currencyStore.formatCurrency(item.price)}</span>
                     </div>
                   {/if}
                 {/each}
              {/each}

              <div class="p-3 flex items-center justify-between bg-surface-50/50">
                <div class="pl-11">
                  <p class="text-xs font-medium text-text-secondary">+ 4 more items</p>
                </div>
                <button class="text-xs font-semibold text-brand-600 flex items-center gap-1">
                  View all <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </div>
         </Card>
      </div>

      <!-- Receipt Thumbnail -->
      <Card class="shadow-md">
        <div class="flex items-center justify-between mb-3 p-4">
          <h2 class="text-sm font-semibold">Receipt</h2>
          <a href="#" class="inline-flex items-center justify-center h-8 px-3 rounded-lg bg-surface-100 text-xs font-semibold text-text-primary hover:bg-surface-200 transition-colors">
            Full View
          </a>
        </div>
        <button type="button" class="w-full rounded-xl border border-surface-200 bg-surface-50 overflow-hidden active:scale-[0.99] transition-transform">
          <div class="relative h-24 bg-surface-100 flex items-center justify-center">
             <div class="flex items-center gap-2 text-text-tertiary">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span class="text-xs font-medium">Receipt_2024.jpg</span>
             </div>
          </div>
        </button>
        <div class="mt-3 grid grid-cols-2 gap-3 text-xs p-4">
          <div class="flex flex-col">
            <span class="text-text-secondary">Date</span>
            <span class="font-semibold text-text-primary">Mar 15, 2024</span>
          </div>
          <div class="flex flex-col">
            <span class="text-text-secondary">Time</span>
            <span class="font-semibold text-text-primary">7:42 PM</span>
          </div>
        </div>
      </Card>
    </section>

    <!-- Breakdown with Payment Status -->
    <Card class="shadow-md overflow-hidden">
      <div class="p-4 flex items-center justify-between gap-3 bg-surface-50/50 border-b border-surface-100">
        <div>
          <h2 class="text-sm font-semibold">Breakdown</h2>
          <p class="text-xs text-text-secondary mt-0.5">Includes tax & tip</p>
        </div>
        <svg class="w-5 h-5 text-text-tertiary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>

      <div class="divide-y divide-slate-100">
        {#each Object.entries(splitData.results) as [name, data]}
          <div class="p-4">
            <div class="flex items-start gap-3">
              <div class={`shrink-0 w-10 h-10 rounded-full ${getPersonColor(name)} flex items-center justify-center font-bold text-sm`}>
                {getPersonInitials(name)}
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <p class="text-sm font-semibold text-text-primary">{name}</p>
                    <PaymentBadge status={paymentStatus[name] || 'pending'} />
                  </div>
                  <p class="text-sm font-bold text-text-primary">{$currencyStore.formatCurrency(data.total)}</p>
                </div>
                <div class="mt-1 flex items-center justify-between">
                   <span class="text-xs text-text-secondary">25% share</span>
                   {#if paymentStatus[name] === 'paid'}
                     <span class="inline-flex items-center gap-1 rounded-full bg-emerald-50 text-emerald-700 px-2 py-0.5 text-xs font-bold border border-emerald-100 uppercase tracking-wide">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg> Paid
                    </span>
                   {:else}
                     <span class="inline-flex items-center gap-1 rounded-full bg-amber-50 text-amber-700 px-2 py-0.5 text-xs font-bold border border-amber-100 uppercase tracking-wide">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg> Unpaid
                    </span>
                   {/if}
                </div>
              </div>
            </div>
            {#if paymentStatus[name] !== 'paid'}
              <Button
                variant="outline"
                size="sm"
                onclick={() => markAsPaid(name)}
                class="mt-3 w-full"
              >
                Mark as Paid
              </Button>
            {/if}
          </div>
        {/each}
      </div>
    </Card>

     <!-- Activity Timeline -->
     <section aria-live="polite">
      <h2 class="text-sm font-semibold text-text-primary mb-3 px-1">Activity</h2>
      <div class="ml-2 pl-4 border-l-2 border-surface-200 space-y-6 relative">
        {#each activityFeed as activity}
          <ActivityFeedItem activity={activity} />
        {/each}
      </div>
    </section>

    <!-- Enhanced Actions -->
    <section>
      <h2 class="text-sm font-semibold text-text-primary mb-3">Actions</h2>

      <!-- Primary Action -->
      <Button variant="primary" onclick={shareSplit} class="w-full h-12 text-base font-semibold mb-3">
        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        Request Payment
      </Button>

      <!-- Secondary Grid -->
      <div class="grid grid-cols-2 gap-3">
        <Button variant="secondary" onclick={() => {}} class="h-12 text-sm font-semibold">
          <svg class="w-5 h-5 mr-2 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Mark Paid
        </Button>

        <Button variant="secondary" onclick={() => showQRCode = !showQRCode} class="h-12 text-sm font-semibold">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
          </svg>
          Share / QR
        </Button>

        <Button variant="secondary" onclick={() => {}} class="h-12 text-sm font-semibold">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Add Note
        </Button>

         <Button variant="secondary" onclick={() => {}} class="h-12 text-sm font-semibold">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          Edit Split
        </Button>
      </div>

      <!-- Navigation Actions -->
      <div class="grid grid-cols-2 gap-3 mt-3">
        <Button variant="secondary" onclick={goHome} class="h-12 text-sm font-semibold">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Go Home
        </Button>

        <Button variant="secondary" onclick={createNewSplit} class="h-12 text-sm font-semibold">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          New Split
        </Button>
      </div>

      <Button variant="danger" onclick={() => {}} class="mt-3 w-full h-12 text-sm font-semibold">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Delete Split
      </Button>

      <!-- Pro Tip -->
      <div class="mt-6 rounded-xl bg-brand-50 border border-brand-100 p-4">
        <div class="flex items-start gap-3">
          <div class="shrink-0 w-8 h-8 rounded-lg bg-surface-0/80 border border-brand-100 text-brand-600 flex items-center justify-center shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm font-semibold text-text-primary">Pro tip</p>
            <p class="mt-1 text-xs text-text-secondary leading-relaxed">
              Send payment requests via Venmo or PayPal links for faster settlements. Everyone can mark themselves as paid to keep the group in sync!
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- QR Code Modal -->
    {#if showQRCode}
      <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <Card class="w-full max-w-md">
          <div class="p-4">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold">Share Split</h3>
              <Button variant="ghost" size="sm" onclick={() => showQRCode = false} ariaLabel="Close">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </Button>
            </div>
            <QRCodeShare
              url={window.location.href}
              title="Split Bill"
              description={`Split with ${splitData.people.join(', ')}`}
            />
            <div class="mt-4">
              <Button variant="secondary" onclick={copyShareLink} class="w-full">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                Copy Share Link
              </Button>
            </div>
          </div>
        </Card>
      </div>
    {/if}
  </div>
{/if}
