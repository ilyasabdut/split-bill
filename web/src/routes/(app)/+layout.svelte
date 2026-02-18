<script lang="ts">
  import AppShell from '$lib/components/layout/AppShell.svelte';
  import OfflineBanner from '$lib/components/layout/OfflineBanner.svelte';
  import ErrorBoundary from '$lib/components/ui/ErrorBoundary.svelte';
  import type { Snippet } from 'svelte';

  interface Props {
    children?: Snippet;
  }

  let { children }: Props = $props();
</script>

<OfflineBanner />
<ErrorBoundary>
  <AppShell>
    {@render children?.()}
  </AppShell>
</ErrorBoundary>
