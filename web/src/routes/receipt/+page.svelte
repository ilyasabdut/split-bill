<script lang="ts">
  import UploadZone from '$lib/components/features/receipt/UploadZone.svelte';
  import type { UploadReceiptResponse } from '$lib/types/api';

  function handleUploadComplete(data: UploadReceiptResponse) {
    // Navigate to split page with receipt data
    window.location.href = `/split?receiptId=${data.receipt_id}`;
  }
</script>

<svelte:head>
  <title>Upload Receipt - Split Bill</title>
</svelte:head>

<UploadZone onUploadComplete={handleUploadComplete} />
