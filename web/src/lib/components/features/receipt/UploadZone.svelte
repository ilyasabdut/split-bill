<script lang="ts">
  import { receiptsService } from '$lib/services/api';
  import { receiptStore } from '$lib/stores/receipt';
  import { offlineStore } from '$lib/stores/offline';
  import { getOfflineQueue } from '$lib/services/offline';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Progress from '$lib/components/ui/Progress.svelte';
  import type { UploadReceiptResponse } from '$lib/types/api';

  interface Props {
    onUploadComplete?: (data: UploadReceiptResponse) => void;
  }

  const { onUploadComplete }: Props = $props();

  let files = $state<FileList | null>(null);
  let uploading = $state(false);
  let progress = $state(0);
  let error = $state<string | null>(null);
  let dragActive = $state(false);

  async function handleUpload() {
    if (!files || files.length === 0) return;

    const file = files[0];

    // Validate
    const validation = receiptsService.validateImage(file);
    if (!validation.valid) {
      error = validation.error || 'Invalid file';
      return;
    }

    error = null;
    uploading = true;
    progress = 0;

    try {
      // Check if offline
      if (!$offlineStore.online) {
        // Queue for background sync
        const queue = await getOfflineQueue();
        await queue.enqueue({
          type: 'receipt_upload',
          data: {
            file,
            onProgress: (p) => { progress = p; }
          }
        });
        error = 'Receipt will be uploaded when you reconnect.';
        return;
      }

      // Upload with progress
      const result = await receiptsService.upload({
        file,
        onProgress: (p) => { progress = p; }
      });

      // Update store
      receiptStore.setData(result.parsed_data);

      if (onUploadComplete) {
        onUploadComplete(result);
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Upload failed';
    } finally {
      uploading = false;
      progress = 0;
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragActive = true;
  }

  function handleDragLeave(e: DragEvent) {
    e.preventDefault();
    dragActive = false;
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragActive = false;
    if (e.dataTransfer?.files) {
      files = e.dataTransfer.files;
    }
  }
</script>

<Card
  class="relative"
  ondragover={handleDragOver}
  ondragleave={handleDragLeave}
  ondrop={handleDrop}
>
  <div class="space-y-4">
    <!-- Upload Area -->
    <div
      class="border-2 border-dashed rounded-lg p-8 text-center transition-colors"
      class:drag-active={dragActive}
    >
      <div class="text-5xl mb-4" aria-hidden="true">📸</div>
      <p class="font-medium mb-2">
        {#if uploading}
          Uploading receipt...
        {:else}
          Drop receipt image here or tap to browse
        {/if}
      </p>
      <input
        type="file"
        accept="image/*"
        bind:files
        disabled={uploading}
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        aria-label="Upload receipt image"
      />
    </div>

    <!-- Progress Bar -->
    {#if uploading}
      <div class="space-y-2">
        <div class="flex justify-between text-sm">
          <span>Uploading...</span>
          <span>{progress}%</span>
        </div>
        <Progress value={progress} />
      </div>
    {/if}

    <!-- Error Message -->
    {#if error}
      <div class="bg-red-50 text-red-800 px-4 py-3 rounded-lg" role="alert">
        {error}
      </div>
    {/if}

    <!-- Upload Button -->
    <Button
      variant="primary"
      disabled={uploading || !files || files.length === 0}
      onclick={handleUpload}
    >
      {uploading ? 'Uploading...' : 'Upload Receipt'}
    </Button>
  </div>
</Card>

<style>
  div:has(.drag-active) {
    border-color: var(--color-primary-500);
    background-color: var(--color-primary-50);
  }
</style>
