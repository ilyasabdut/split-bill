<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';
  import { analyticsStore, currencyStore } from '$lib/stores';
  import type { SplitResults } from '$lib/types/split';

  interface HistoryItem {
    id: string;
    createdAt: number;
    people: string[];
    total: number;
    results: SplitResults;
    currency?: string;
    group?: string;
  }

  let history = $state<HistoryItem[]>([]);
  let filteredHistory = $state<HistoryItem[]>([]);
  let loading = $state(true);
  let searchTerm = $state('');
  let dateFilter = $state<'all' | 'week' | 'month' | 'year'>('all');
  let activeTab = $state<'history' | 'analytics'>('history');
  let monthlySpending = $state<any>(null);
  let settlementSummary = $state<any>(null);

  $: {
    // Filter history based on search and date filter
    filteredHistory = history.filter(item => {
      const matchesSearch = searchTerm === '' ||
        item.people.some(p => p.toLowerCase().includes(searchTerm.toLowerCase()));

      if (!matchesSearch) return false;

      if (dateFilter === 'all') return true;

      const now = new Date();
      const itemDate = new Date(item.createdAt);
      const diffDays = Math.floor((now.getTime() - itemDate.getTime()) / (1000 * 60 * 60 * 24));

      switch (dateFilter) {
        case 'week': return diffDays <= 7;
        case 'month': return diffDays <= 30;
        case 'year': return diffDays <= 365;
        default: return true;
      }
    });
  }

  onMount(async () => {
    try {
      await Promise.all([
        currencyStore.init(),
        analyticsStore.loadAnalytics()
      ]);

      const indexedDB = await getIndexedDB();
      const items = await indexedDB.getAll<any>(STORES.SPLITS);

      // Sort by createdAt descending
      history = items
        .filter(item => item.createdAt)
        .sort((a, b) => b.createdAt - a.createdAt)
        .map(item => ({
          id: item.id,
          createdAt: item.createdAt,
          people: Object.keys(item.results || {}),
          total: Object.values(item.results || {}).reduce((sum: number, person: any) => sum + person.total, 0),
          results: item.results,
          currency: item.currency || 'USD',
          group: item.group
        }));

      // Load analytics data
      monthlySpending = analyticsStore.getMonthlySpending();
      settlementSummary = analyticsStore.getSettlementSummary();
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      loading = false;
    }
  });

  function formatDate(timestamp: number): string {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function viewSplit(id: string) {
    window.location.href = `/split/${id}`;
  }
</script>

<svelte:head>
  <title>History - Split Bill</title>
</svelte:head>

<div class="space-y-4">
  <!-- Header with Tabs -->
  <div class="flex justify-between items-center">
    <h2 class="text-xl font-semibold">Split History</h2>
    <div class="flex bg-surface-100 rounded-lg p-1">
      <button
        class="px-3 py-1 rounded text-sm font-medium transition-colors"
        class:bg-white={activeTab === 'history'}
        class:text-text-primary={activeTab === 'history'}
        class:text-text-secondary={activeTab !== 'history'}
        onclick={() => activeTab = 'history'}
      >
        History
      </button>
      <button
        class="px-3 py-1 rounded text-sm font-medium transition-colors"
        class:bg-white={activeTab === 'analytics'}
        class:text-text-primary={activeTab === 'analytics'}
        class:text-text-secondary={activeTab !== 'analytics'}
        onclick={() => activeTab = 'analytics'}
      >
        Analytics
      </button>
    </div>
  </div>

  {#if loading}
    <Card>
      <div class="text-center py-8">
        <p class="text-text-secondary">Loading history...</p>
      </div>
    </Card>
  {:else if activeTab === 'history'}
    <!-- Filters -->
    <Card>
      <div class="space-y-3">
        <Input
          type="search"
          placeholder="Search by name..."
          bind:value={searchTerm}
        />
        <div class="flex gap-2">
          <Button
            variant={dateFilter === 'all' ? 'primary' : 'outline'}
            size="sm"
            onclick={() => dateFilter = 'all'}
          >
            All Time
          </Button>
          <Button
            variant={dateFilter === 'week' ? 'primary' : 'outline'}
            size="sm"
            onclick={() => dateFilter = 'week'}
          >
            This Week
          </Button>
          <Button
            variant={dateFilter === 'month' ? 'primary' : 'outline'}
            size="sm"
            onclick={() => dateFilter = 'month'}
          >
            This Month
          </Button>
          <Button
            variant={dateFilter === 'year' ? 'primary' : 'outline'}
            size="sm"
            onclick={() => dateFilter = 'year'}
          >
            This Year
          </Button>
        </div>
      </div>
    </Card>

    {#if filteredHistory.length === 0}
      <Card>
        <div class="text-center py-8">
          <div class="text-5xl mb-4" aria-hidden="true">📋</div>
          <h3 class="font-semibold mb-2">No splits found</h3>
          <p class="text-text-secondary mb-4">Try adjusting your filters or create a new split.</p>
          <div class="flex gap-2 justify-center">
            <Button variant="primary" onclick={() => window.location.href = '/receipt'}>
              Upload Receipt
            </Button>
            <Button variant="secondary" onclick={() => window.location.href = '/split'}>
              New Split
            </Button>
          </div>
        </div>
      </Card>
    {:else}
      <div class="space-y-3">
        {#each filteredHistory as item}
          <Card class="hover:bg-surface-50 transition-colors cursor-pointer" onclick={() => viewSplit(item.id)}>
            <div class="flex justify-between items-center">
              <div class="flex-1">
                <div class="flex justify-between items-start mb-2">
                  <h3 class="font-semibold">{item.people.join(', ')}</h3>
                  <span class="text-lg font-bold text-primary-600">
                    {currencyStore.formatCurrency(item.total)}
                  </span>
                </div>
                <p class="text-sm text-text-secondary">
                  {item.people.length} people • {formatDate(item.createdAt)}
                </p>
                {#if item.group}
                  <p class="text-xs text-text-secondary mt-1">Group: {item.group}</p>
                {/if}
              </div>
              <div class="ml-4">
                <span class="text-2xl" aria-hidden="true">→</span>
              </div>
            </div>
          </Card>
        {/each}
      </div>
    {/if}
  {:else if activeTab === 'analytics'}
    <!-- Settlement Summary -->
    {#if settlementSummary}
      <Card>
        <h3 class="text-lg font-semibold mb-4">Settlement Summary</h3>
        <div class="space-y-3">
          {#each Object.entries(settlementSummary) as [person, data]}
            <div class="flex justify-between items-center p-3 bg-surface-50 rounded-lg">
              <span class="font-medium">{person}</span>
              <span class={`font-bold ${data.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {data.amount > 0 ? 'Receives' : 'Owes'} {currencyStore.formatCurrency(Math.abs(data.amount))}
              </span>
            </div>
          {/each}
        </div>
      </Card>
    {/if}

    <!-- Monthly Spending -->
    {#if monthlySpending}
      <Card>
        <h3 class="text-lg font-semibold mb-4">Monthly Spending</h3>
        <div class="space-y-3">
          {#each Object.entries(monthlySpending).slice(-6) as [month, amount]}
            <div class="flex justify-between items-center">
              <span class="text-sm">{month}</span>
              <span class="font-semibold">{currencyStore.formatCurrency(amount)}</span>
            </div>
          {/each}
        </div>
      </Card>
    {/if}

    <!-- Export Options -->
    <Card>
      <h3 class="text-lg font-semibold mb-4">Export Data</h3>
      <div class="flex gap-2">
        <Button variant="outline" onclick={() => analyticsStore.exportData('csv')}>
          Export CSV
        </Button>
        <Button variant="outline" onclick={() => analyticsStore.exportData('json')}>
          Export JSON
        </Button>
      </div>
    </Card>
  {/if}
</div>
