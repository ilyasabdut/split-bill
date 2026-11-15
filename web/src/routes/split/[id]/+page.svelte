<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import SettlementGraph from '$lib/components/SettlementGraph.svelte';
  import PaymentBadge from '$lib/components/PaymentBadge.svelte';
  import QRCodeShare from '$lib/components/QRCodeShare.svelte';
  import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';
  import { splitsService } from '$lib/services/api';
  import { currencyStore } from '$lib/stores/currency';
  import { get } from 'svelte/store';
  import type { SplitResults, PersonSplit } from '$lib/types/split';

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
  let paymentStatus = $state<Record<string, 'pending' | 'paid'>>({});

  const splitId = $derived($page.params.id);

  let dataLoaded = $state(false);

  $effect(() => {
    if (splitId && !dataLoaded) {
      dataLoaded = true;
      loadSplitData();
    }
  });

  async function loadSplitData() {
    const id = $page.params.id;
    if (!id) {
      error = 'Invalid split link';
      loading = false;
      return;
    }

    currencyStore.init();

    try {
      const db = await getIndexedDB();
      const localData = await db.get<any>(STORES.SPLITS, id);

      if (localData) {
        const total = Object.values(localData.results).reduce((sum: number, person: any) => sum + person.total, 0);
        splitData = {
          results: localData.results,
          createdAt: localData.createdAt,
          people: Object.keys(localData.results),
          total,
          receiptData: localData.receipt_data
        };

        // Restore saved payment status
        if (localData.payments) {
          paymentStatus = { ...localData.payments };
        }
      } else {
        // Not created on this device: it is a shared link, load it from the server
        const shared = await splitsService.getShared(id);
        const results = shared.calculated_split_results as SplitResults;
        splitData = {
          results,
          createdAt: shared.creation_timestamp * 1000,
          people: shared.person_names,
          total: Object.values(results).reduce((sum, person) => sum + person.total, 0)
        };
      }
    } catch (err) {
      error = 'Split not found. It may have expired or the link is invalid.';
    } finally {
      loading = false;
    }
  }

  async function markAsPaid(personName: string) {
    if (!splitId) return;
    try {
      paymentStatus[personName] = 'paid';
      paymentStatus = { ...paymentStatus };

      // Persist to IndexedDB
      const db = await getIndexedDB();
      const localData = await db.get<any>(STORES.SPLITS, splitId);
      if (localData) {
        localData.payments = { ...(localData.payments || {}), [personName]: 'paid' };
        await db.put(STORES.SPLITS, localData);
      }

    } catch (err) {
      paymentStatus[personName] = 'pending';
      paymentStatus = { ...paymentStatus };
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

  function computeSettlements(): { from: string; to: string; amount: number; currency: string }[] {
    if (!splitData) return [];
    const people = Object.keys(splitData.results);
    if (people.length < 2) return [];

    const payer = people[0];
    const settlements: { from: string; to: string; amount: number; currency: string }[] = [];

    for (const person of people) {
      if (person === payer) continue;
      const personData = splitData.results[person];
      if (personData.total > 0) {
        settlements.push({
          from: person,
          to: payer,
          amount: personData.total,
          currency: 'IDR'
        });
      }
    }

    return settlements;
  }

  const settlements = $derived(computeSettlements());

  const totalReceivable = $derived(() => {
    if (!splitData) return 0;
    const people = Object.keys(splitData.results);
    const payer = people[0];
    return people
      .filter(p => p !== payer)
      .reduce((sum, p) => sum + splitData!.results[p].total, 0);
  });

  const totalItemCount = $derived(() => {
    if (!splitData) return 0;
    return Object.values(splitData.results).reduce((sum, p) => sum + p.items.length, 0);
  });

  const shownItemCount = $derived(() => {
    if (!splitData) return 0;
    return Object.values(splitData.results).reduce((sum, p) => sum + Math.min(2, p.items.length), 0);
  });

  function formatCurrency(amount: number): string {
    const symbols: Record<string, string> = {
      'IDR': 'Rp', 'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'NZD': '$'
    };
    const code = get(currencyStore).selected;
    const symbol = symbols[code] || 'Rp';
    const hasDecimals = code !== 'JPY' && code !== 'IDR';
    const formatter = new Intl.NumberFormat('en-US', {
      minimumFractionDigits: hasDecimals ? 2 : 0,
      maximumFractionDigits: hasDecimals ? 2 : 0
    });
    if (amount < 0) return `-${symbol}${formatter.format(Math.abs(amount))}`;
    return `${symbol}${formatter.format(amount)}`;
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
        <h1 class="mt-1 text-lg font-semibold leading-tight truncate">{splitData?.receiptData?.merchant || splitData?.people.join(', ') || 'Bill Split'}</h1>
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
            <p class="text-3xl font-semibold tracking-tight">{formatCurrency(splitData.total)}</p>
            <span class="text-sm font-medium text-text-tertiary">IDR</span>
          </div>

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
          {#each Object.entries(splitData.results) as [name, data] (name)}
                {@const personData = data as PersonSplit}
            {#if name !== splitData.people[0]}
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
                  <span class="text-sm font-bold text-text-primary">{formatCurrency(personData.total)}</span>
                  <svg class="w-4 h-4 text-text-tertiary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </div>
              </div>
            {/if}
          {/each}
        </div>
        <div class="bg-surface-50 px-4 py-2 border-t border-surface-200 text-center">
           <p class="text-xs text-text-secondary">Total receivable: <span class="font-semibold text-text-primary">{formatCurrency(totalReceivable())}</span></p>
        </div>
      </Card>
    </section>

    <!-- Settlement Graph -->
    <section>
      <h2 class="text-sm font-semibold text-text-primary mb-3 px-1">Settlement Graph</h2>
      <Card class="shadow-md">
        <div class="p-4">
          <SettlementGraph {settlements} />
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
              {#each Object.entries(splitData.results) as [name, data] (name)}
                {@const personData = data as PersonSplit}
                {#each personData.items as item, index}
                  {#if index < 2}
                    <div class="p-3 flex items-center justify-between">
                      <div class="flex items-center gap-3">
                        <span class="w-8 h-8 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        </span>
                        <div>
                          <p class="text-sm font-medium text-text-primary">{item.name}</p>
                          <p class="text-xs text-text-secondary">{name}</p>
                        </div>
                      </div>
                      <span class="text-sm font-semibold text-text-primary">{formatCurrency(item.price)}</span>
                    </div>
                  {/if}
                {/each}
              {/each}

              {#if totalItemCount() > shownItemCount()}
                <div class="p-3 flex items-center justify-between bg-surface-50/50">
                  <div class="pl-11">
                    <p class="text-xs font-medium text-text-secondary">+ {totalItemCount() - shownItemCount()} more items</p>
                  </div>
                  <button class="text-xs font-semibold text-brand-600 flex items-center gap-1">
                    View all <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              {/if}
            </div>
         </Card>
      </div>

      <!-- Receipt Thumbnail -->
      <Card class="shadow-md">
        <div class="flex items-center justify-between mb-3 p-4">
          <h2 class="text-sm font-semibold">Receipt</h2>
          <button type="button" class="inline-flex items-center justify-center h-8 px-3 rounded-lg bg-surface-100 text-xs font-semibold text-text-primary hover:bg-surface-200 transition-colors">
            Full View
          </button>
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
        {#each Object.entries(splitData.results) as [name, data] (name)}
                {@const personData = data as PersonSplit}
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
                  <p class="text-sm font-bold text-text-primary">{formatCurrency(personData.total)}</p>
                </div>
                <div class="mt-1 flex items-center justify-between">
                   <span class="text-xs text-text-secondary">{Math.round((personData.total / splitData.total) * 100)}% share</span>
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
              data={window.location.href}
              title="Split Bill"
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
