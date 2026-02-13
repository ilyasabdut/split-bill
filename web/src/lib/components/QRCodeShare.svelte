<script lang="ts">
  import { onMount } from 'svelte';
  import Button from './ui/Button.svelte';

  interface Props {
    data: string;
    size?: number;
    class?: string;
    showDownload?: boolean;
    showCopy?: boolean;
    title?: string;
  }

  const {
    data,
    size = 256,
    class: className = '',
    showDownload = true,
    showCopy = true,
    title = 'Share via QR Code'
  }: Props = $props();

  let qrCodeUrl = $state<string>('');
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    // Generate QR code using qrcode library
    try {
      const QRCode = await import('qrcode');
      qrCodeUrl = await QRCode.toDataURL(data, {
        width: size,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });
    } catch (err) {
      error = 'Failed to generate QR code';
      console.error('Failed to generate QR code:', err);
    } finally {
      loading = false;
    }
  });

  function downloadQR() {
    if (!qrCodeUrl) return;

    const link = document.createElement('a');
    link.download = `qr-code-${Date.now()}.png`;
    link.href = qrCodeUrl;
    link.click();
  }

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(data);
      // You might want to show a toast notification here
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }
</script>

<div class="bg-surface-100 rounded-xl p-6 {className}">
  {#if title}
    <h3 class="text-lg font-semibold text-text mb-4 text-center">{title}</h3>
  {/if}

  {#if loading}
    <div class="flex items-center justify-center py-8">
      <div class="text-center">
        <div class="w-12 h-12 mx-auto mb-3">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
        <p class="text-text-secondary">Generating QR code...</p>
      </div>
    </div>
  {:else if error}
    <div class="text-center py-8">
      <svg class="w-12 h-12 text-red-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-red-600">{error}</p>
    </div>
  {:else if qrCodeUrl}
    <div class="flex flex-col items-center space-y-4">
      <!-- QR Code -->
      <div class="bg-white p-4 rounded-lg shadow-sm">
        <img src={qrCodeUrl} alt="QR Code" class="w-full h-auto" style="max-width: {size}px" />
      </div>

      <!-- Data preview -->
      <div class="w-full bg-surface-50 rounded-lg p-3 text-center">
        <p class="text-xs text-text-secondary mb-1">Encoded data:</p>
        <p class="text-sm text-text font-mono break-all">{data}</p>
      </div>

      <!-- Actions -->
      {#if showDownload || showCopy}
        <div class="flex gap-2">
          {#if showDownload}
            <Button variant="primary" size="sm" onclick={downloadQR}>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" slot="icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </Button>
          {/if}

          {#if showCopy}
            <Button variant="secondary" size="sm" onclick={copyToClipboard}>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" slot="icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy Link
            </Button>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>
