<script lang="ts">
  import UploadZone from '$lib/components/features/receipt/UploadZone.svelte';
  import type { UploadReceiptResponse } from '$lib/types/api';
  import { receiptStore } from '$lib/stores/receipt';

  let loading = $state(false);
  let error = $state<string | null>(null);

  function handleUploadComplete(data: UploadReceiptResponse) {
    // Navigate to split page with receipt data
    window.location.href = `/split?receiptId=${data.receipt_id}`;
  }
</script>

<svelte:head>
  <title>Upload Receipt - Split Bill</title>
</svelte:head>

<div class="space-y-4">
  <!-- Loading Skeleton -->
  {#if loading}
    <div class="animate-pulse space-y-4">
      <div class="bg-white rounded-xl shadow-sm border border-surface-200 p-6">
        <div class="flex items-center justify-center mb-4">
          <div class="w-12 h-12 rounded-full bg-surface-100 animate-pulse"></div>
        </div>
        <div class="space-y-3">
          <div class="h-4 bg-surface-100 rounded"></div>
          <div class="h-4 bg-surface-100 rounded w-3/4"></div>
          <div class="h-4 bg-surface-100 rounded w-1/2"></div>
        </div>
      </div>
      <p class="text-center text-text-secondary">Processing receipt...</p>
    </div>
  {/if}

  <!-- Error Message -->
  {#if error}
    <div class="bg-red-50 text-red-800 px-4 py-3 rounded-lg" role="alert">
      <p class="font-medium">{error}</p>
    </div>
  {/if}

  <!-- Upload Component -->
  <UploadZone
    onUploadComplete={(data) => {
      loading = true;
      error = null;
      receiptStore.setData(data.parsed_data);
      // Navigate after a brief delay to show loading state
      setTimeout(() => handleUploadComplete(data), 500);
    }}
  />
</div>
