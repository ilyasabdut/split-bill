<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import BottomNav from '$lib/components/layout/BottomNav.svelte';
  import type { Snippet } from 'svelte';

  interface Props {
    children?: Snippet;
  }

  let { children }: Props = $props();
  let currentPath = $derived($page.url.pathname);

  const hideNavPaths = ['/split/'];

  onMount(() => {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
      document.documentElement.classList.add('dark');
    }
  });
</script>

<div class="min-h-screen flex justify-center bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-sans">
  <div class="w-full max-w-[430px] min-h-screen flex flex-col relative">
    {@render children?.()}
  </div>
</div>

{#if !hideNavPaths.some(p => currentPath.startsWith(p) && currentPath !== '/split')}
  <BottomNav currentPath={currentPath} />
{/if}
