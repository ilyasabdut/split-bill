<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  import BottomNav from '$lib/components/layout/BottomNav.svelte';
  import type { Snippet } from 'svelte';

  interface Props {
    children?: Snippet;
  }

  let { children }: Props = $props();
  let currentPath = $derived($page.url.pathname);

  const hideNavPaths = ['/split/'];
</script>

<div class="flex flex-col min-h-dvh bg-slate-50 text-slate-900 font-sans overflow-x-hidden">
  {@render children?.()}
</div>

{#if !hideNavPaths.some(p => currentPath.startsWith(p) && currentPath !== '/split')}
  <BottomNav currentPath={currentPath} />
{/if}
