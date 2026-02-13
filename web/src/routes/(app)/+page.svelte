<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import CurrencySelector from '$lib/components/CurrencySelector.svelte';
  import TemplateCard from '$lib/components/TemplateCard.svelte';
  import GroupCard from '$lib/components/GroupCard.svelte';
  import ActivityFeedItem from '$lib/components/ActivityFeedItem.svelte';
  import { currencyStore } from '$lib/stores/currency';
  import { templatesStore } from '$lib/stores/templates';
  import { groupsStore } from '$lib/stores/groups';
  import { analyticsStore } from '$lib/stores/analytics';
  import { splitStore } from '$lib/stores/split';
  import { goto } from '$app/navigation';

  let recentActivity = [];
  let spendingInsights = null;

  onMount(async () => {
    // Load initial data
    await Promise.all([
      currencyStore.init(),
      templatesStore.loadTemplates(),
      groupsStore.loadGroups(),
      analyticsStore.loadAnalytics()
    ]);

    // Get recent activity and insights
    recentActivity = await splitStore.getRecentSplits(5);
    spendingInsights = analyticsStore.getSpendingInsights();
  });

  function createSplitFromTemplate(template: any) {
    goto(`/split?template=${template.id}`);
  }

  function createSplitWithGroup(group: any) {
    goto(`/split?group=${group.id}`);
  }
</script>

<svelte:head>
  <title>Split Bill - Home</title>
</svelte:head>

<div class="space-y-6">
  <!-- Welcome Section -->
  <Card>
    <div class="flex justify-between items-start mb-2">
      <div>
        <h2 class="text-lg font-semibold">Welcome to Split Bill</h2>
        <p class="text-text-secondary">Split bills easily with friends using your phone.</p>
      </div>
      <CurrencySelector />
    </div>
  </Card>

  <!-- Quick Actions -->
  <div class="grid grid-cols-2 gap-4">
    <a href="/receipt">
      <Card class="text-center hover:bg-surface-50 transition-colors cursor-pointer">
        <div class="text-4xl mb-2" aria-hidden="true">📸</div>
        <h3 class="font-semibold">Upload Receipt</h3>
        <p class="text-sm text-text-secondary">Scan or upload</p>
      </Card>
    </a>

    <a href="/split">
      <Card class="text-center hover:bg-surface-50 transition-colors cursor-pointer">
        <div class="text-4xl mb-2" aria-hidden="true">💰</div>
        <h3 class="font-semibold">New Split</h3>
        <p class="text-sm text-text-secondary">Create a split</p>
      </Card>
    </a>
  </div>

  <!-- Spending Insights -->
  {#if spendingInsights}
    <Card>
      <h3 class="text-lg font-semibold mb-4">Spending Insights</h3>
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <p class="text-2xl font-bold text-primary">{spendingInsights.thisMonth}</p>
          <p class="text-sm text-text-secondary">This Month</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary">{spendingInsights.avgSplit}</p>
          <p class="text-sm text-text-secondary">Avg Split</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary">{spendingInsights.totalSplits}</p>
          <p class="text-sm text-text-secondary">Total Splits</p>
        </div>
      </div>
    </Card>
  {/if}

  <!-- Recent Activity -->
  {#if recentActivity.length > 0}
    <Card>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Recent Activity</h3>
        <a href="/history" class="text-sm text-primary hover:underline">View All</a>
      </div>
      <div class="space-y-3">
        {#each recentActivity as activity}
          <ActivityFeedItem {activity} />
        {/each}
      </div>
    </Card>
  {/if}

  <!-- Groups -->
  {#if $groupsStore.groups.length > 0}
    <Card>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Your Groups</h3>
        <Button variant="outline" size="sm" href="/settings#groups">Manage</Button>
      </div>
      <div class="grid gap-3">
        {#each $groupsStore.groups.slice(0, 3) as group}
          <GroupCard
            {group}
            on:click={() => createSplitWithGroup(group)}
            showActions={false}
          />
        {/each}
      </div>
    </Card>
  {/if}

  <!-- Templates -->
  {#if $templatesStore.templates.length > 0}
    <Card>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Quick Templates</h3>
        <Button variant="outline" size="sm" href="/settings#templates">Manage</Button>
      </div>
      <div class="grid gap-3">
        {#each $templatesStore.templates.slice(0, 3) as template}
          <TemplateCard
            {template}
            on:click={() => createSplitFromTemplate(template)}
            showActions={false}
          />
        {/each}
      </div>
    </Card>
  {/if}
</div>
