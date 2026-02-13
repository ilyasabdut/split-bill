<script lang="ts">
  import AppShell from '$lib/components/layout/AppShell.svelte';
  import OfflineBanner from '$lib/components/layout/OfflineBanner.svelte';
  import BottomNav from '$lib/components/layout/BottomNav.svelte';
  import ErrorBoundary from '$lib/components/ui/ErrorBoundary.svelte';
  import { page } from '$app/stores';

  let currentPath = $state(page.url.pathname);
  $effect(() => {
    currentPath = page.url.pathname;
  });
</script>

<OfflineBanner />
<ErrorBoundary>
  <AppShell>
    <slot />
  </AppShell>
</ErrorBoundary>
<BottomNav currentPath={currentPath} />
