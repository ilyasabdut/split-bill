<script lang="ts">
  import type { Snippet } from 'svelte';
  import { cn } from '$lib/utils';

  interface Props {
    title?: string;
    class?: string;
    children?: Snippet;
  }

  const { title = 'Split Bill', class: className = '', children }: Props = $props();
</script>

<div class="flex flex-col min-h-dvh bg-surface pb-[60px] overflow-x-hidden">
  <!-- Header -->
  <header class="sticky top-0 z-header bg-white border-b border-surface-200 px-4 py-3 w-full">
    <h1 class="text-xl font-semibold text-text text-balance">{title}</h1>
  </header>

  <!-- Main Content -->
  <main class={cn('flex-1 px-4 py-4 w-full', className)}>
    {#if children}
      {@render children()}
    {/if}
  </main>
</div>
