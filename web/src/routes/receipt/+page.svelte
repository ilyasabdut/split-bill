<script lang="ts">
  import UploadZone from '$lib/components/features/receipt/UploadZone.svelte';
  import CurrencySelector from '$lib/components/CurrencySelector.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Progress from '$lib/components/ui/Progress.svelte';
  import type { UploadReceiptResponse } from '$lib/types/api';
  import { receiptStore } from '$lib/stores/receipt';
  import { currencyStore } from '$lib/stores/currency';
  import { onMount } from 'svelte';

  let loading = $state(false);
  let error = $state<string | null>(null);
  let uploadResult = $state<UploadReceiptResponse | null>(null);
  let showItemDetection = $state(false);

  onMount(async () => {
    await currencyStore.init();
  });

  function handleUploadComplete(data: UploadReceiptResponse) {
    uploadResult = data;
    loading = false;

    // Show item detection if items were found
    if (data.parsed_data?.items && data.parsed_data.items.length > 0) {
      showItemDetection = true;
    } else {
      // Navigate to split page with receipt data
      setTimeout(() => {
        window.location.href = `/split?receiptId=${data.receipt_id}`;
      }, 1000);
    }
  }

  function confirmItems() {
    if (uploadResult) {
      receiptStore.setData(uploadResult.parsed_data);
      window.location.href = `/split?receiptId=${uploadResult.receipt_id}`;
    }
  }

  function editItems() {
    showItemDetection = false;
    // Allow manual editing
  }
</script>

<svelte:head>
  <title>Upload Receipt - Split Bill</title>
</svelte:head>

<div class="space-y-4">
  <!-- Currency Selector -->
  <div class="flex justify-end">
    <CurrencySelector />
  </div>

  <!-- Loading State -->
  {#if loading}
    <Card>
      <div class="text-center space-y-4">
        <div class="text-5xl mb-4" aria-hidden="true">🤖</div>
        <h3 class="text-lg font-semibold">Processing Receipt</h3>
        <Progress value={75} />
        <p class="text-text-secondary">Detecting items and calculating totals...</p>
      </div>
    </Card>
  {/if}

  <!-- Error Message -->
  {#if error}
    <div class="bg-red-50 text-red-800 px-4 py-3 rounded-lg" role="alert">
      <p class="font-medium">{error}</p>
    </div>
  {/if}

  <!-- Item Detection Results -->
  {#if showItemDetection && uploadResult?.parsed_data}
    <Card>
      <h3 class="text-lg font-semibold mb-4">Detected Items</h3>

      <!-- Tax Recognition -->
      {#if uploadResult.parsed_data.tax}
        <div class="mb-4 p-3 bg-green-50 rounded-lg">
          <p class="text-sm text-green-800">
            <span class="font-semibold">Tax detected:</span> {currencyStore.formatCurrency(uploadResult.parsed_data.tax)}
          </p>
        </div>
      {/if}

      <!-- Items List -->
      <div class="space-y-3 mb-4">
        {#each uploadResult.parsed_data.items || [] as item, i}
          <div class="flex justify-between items-center p-3 bg-surface-50 rounded-lg">
            <div class="flex-1">
              <p class="font-medium">{item.name}</p>
              <p class="text-sm text-text-secondary">{currencyStore.formatCurrency(item.price)}</p>
            </div>
            <div class="text-right">
              <span class="text-xs text-text-secondary">Confidence: {Math.round((item.confidence || 0.8) * 100)}%</span>
            </div>
          </div>
        {/each}
      </div>

      <!-- Total -->
      <div class="border-t pt-4 mb-4">
        <div class="flex justify-between items-center">
          <span class="font-semibold">Total:</span>
          <span class="text-xl font-bold text-primary">
            {currencyStore.formatCurrency(uploadResult.parsed_data.total)}
          </span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="grid grid-cols-2 gap-3">
        <Button variant="outline" onclick={editItems}>Edit Items</Button>
        <Button variant="primary" onclick={confirmItems}>Continue to Split</Button>
      </div>
    </Card>
  {/if}

  <!-- Upload Component -->
  {#if !showItemDetection}
    <UploadZone
      onUploadComplete={(data) => {
        loading = true;
        error = null;
        setTimeout(() => handleUploadComplete(data), 1500);
      }}
    />
  {/if}
</div>
