<script lang="ts">
  import '../../app.css';
  import AppShell from '$lib/components/layout/AppShell.svelte';
  import OfflineBanner from '$lib/components/layout/OfflineBanner.svelte';
  import BottomNav from '$lib/components/layout/BottomNav.svelte';
  import ErrorBoundary from '$lib/components/ui/ErrorBoundary.svelte';
  import { page } from '$app/stores';
  import type { Snippet } from 'svelte';

  interface Props {
    children?: Snippet;
  }

  let { children }: Props = $props();
  let currentPath = $derived($page.url.pathname);
</script>

<OfflineBanner />
<ErrorBoundary>
  <AppShell>
    {@render children?.()}
  </AppShell>
</ErrorBoundary>
<BottomNav currentPath={currentPath} />
