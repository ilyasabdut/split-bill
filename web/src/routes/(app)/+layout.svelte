<script lang="ts">
  import AppShell from '$lib/components/layout/AppShell.svelte';
  import OfflineBanner from '$lib/components/layout/OfflineBanner.svelte';
  import BottomNav from '$lib/components/layout/BottomNav.svelte';
  import { page } from '$app/stores';

  let currentPath = $state(page.url.pathname);
  $effect(() => {
    currentPath = page.url.pathname;
  });
</script>

<OfflineBanner />
<AppShell>
  <slot />
</AppShell>
<BottomNav currentPath={currentPath} />
