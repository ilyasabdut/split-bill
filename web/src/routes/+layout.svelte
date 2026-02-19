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

<div class="min-h-screen flex justify-center bg-slate-50 text-slate-900 font-sans">
  <div class="w-full max-w-[430px] min-h-screen flex flex-col relative">
    {@render children?.()}
  </div>
</div>

{#if !hideNavPaths.some(p => currentPath.startsWith(p) && currentPath !== '/split')}
  <BottomNav currentPath={currentPath} />
{/if}
