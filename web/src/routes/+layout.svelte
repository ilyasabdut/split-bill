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

<div class="min-h-screen flex justify-center bg-surface-50 dark:bg-surface-900 text-text-primary dark:text-text-primary font-sans">
  <!-- Skip link for keyboard users -->
  <a href="#main-content" class="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary-500 focus:text-white focus:rounded-lg focus:font-semibold">
    Skip to content
  </a>
  <div class="w-full max-w-[430px] min-h-screen flex flex-col relative">
    <main id="main-content" class="flex-1">
      {@render children?.()}
    </main>
  </div>
</div>

{#if !hideNavPaths.some(p => currentPath.startsWith(p) && currentPath !== '/split')}
  <BottomNav currentPath={currentPath} />
{/if}
