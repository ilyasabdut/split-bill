<script lang="ts">
  import { isOffline } from '$lib/stores/offline';
  import { cn } from '$lib/utils';
</script>

{#if $isOffline}
<div class={cn('fixed top-0 left-0 right-0 z-offline-banner bg-yellow-100 text-yellow-800 px-4 py-3 flex items-center gap-3 shadow-md', 'safe-area-inset-top')} role="alert">
  <span class="text-xl" aria-hidden="true">📡</span>
  <span class="flex-1 text-sm font-medium text-balance">
    You're offline. Splits are saved on this device.
  </span>
</div>
{/if}
