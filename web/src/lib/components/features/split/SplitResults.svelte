<script lang="ts">
  import type { SplitResults } from '$lib/types/split';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  interface Props {
    results: SplitResults;
    splitId?: string;
  }

  const { results, splitId }: Props = $props();

  const shareUrl = $derived(splitId ? `${window.location.origin}/split/${splitId}` : (typeof window !== 'undefined' ? window.location.href : ''));

  async function copyShareLink() {
    await navigator.clipboard.writeText(shareUrl);
  }

  const totalAmount = $derived(Object.values(results).reduce((sum, r) => sum + r.total, 0));
</script>

<Card>
  <div class="space-y-4">
    <h2 class="text-lg font-semibold">Split Results</h2>

    <div class="text-center p-4 bg-primary-50 rounded-lg">
      <p class="text-sm text-primary-700">Total</p>
      <p class="text-3xl font-bold text-primary-700">${totalAmount.toFixed(2)}</p>
    </div>

    <!-- Per-Person Breakdown -->
    <div class="space-y-2">
      {#each Object.entries(results) as [name, data]}
        <div class="p-3 bg-surface-50 rounded-lg">
          <div class="flex justify-between items-center mb-2">
            <h3 class="font-semibold">{name}</h3>
            <span class="text-lg font-bold">${data.total.toFixed(2)}</span>
          </div>
          <p class="text-sm text-text-secondary">
            {data.items.length} items · Tax: ${data.tax_share.toFixed(2)} · Tip: ${data.tip_share.toFixed(2)}
          </p>
        </div>
      {/each}
    </div>

    <!-- Share Actions -->
    <div class="flex gap-2">
      <Button variant="primary" onclick={copyShareLink} class="flex-1">
        📋 Copy Link
      </Button>
    </div>
  </div>
</Card>
