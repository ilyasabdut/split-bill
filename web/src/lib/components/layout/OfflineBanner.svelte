<script lang="ts">
  import { offlineStore } from '$lib/stores/offline';

  const isOffline = $derived(() => !$offlineStore.online);
  const hasQueuedActions = $derived(() => $offlineStore.queuedActions > 0);
</script>

{#if $isOffline}
<div class="fixed top-0 left-0 right-0 z-50 bg-yellow-100 text-yellow-800 px-4 py-3 flex items-center gap-3 shadow-md" role="alert">
  <span class="text-xl" aria-hidden="true">📡</span>
  <span class="flex-1 text-sm font-medium">
    You're offline. Actions will be synced when connection returns.
  </span>
  {#if $hasQueuedActions}
    <span class="px-2 py-1 bg-red-600 text-white text-xs font-semibold rounded-full">
      {$offlineStore.queuedActions} pending
    </span>
  {/if}
</div>
{/if}
