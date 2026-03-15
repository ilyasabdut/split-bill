<script lang="ts">
  import type { Snippet } from 'svelte';
  import { cn } from '$lib/utils';

  interface Props {
    title?: string;
    class?: string;
    children?: Snippet;
    showHeader?: boolean;
  }

  const { title = 'Split Bill', class: className = '', children, showHeader = true }: Props = $props();
</script>

<div class="flex flex-col min-h-dvh bg-surface-50 overflow-x-hidden">
  {#if showHeader}
    <header
      class="sticky top-0 z-header bg-surface-0 border-b border-surface-200 w-full px-safe py-3"
      style="padding-top: max(env(safe-area-inset-top), 0.75rem);"
    >
      <div class="max-w-[430px] mx-auto">
        <h1 class="text-xl font-semibold text-text-primary text-balance">{title}</h1>
      </div>
    </header>
  {/if}

  <main
    class={cn('flex-1 w-full px-safe', className)}
    style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 80px);"
  >
    <div class="max-w-[430px] mx-auto py-4">
      {#if children}
        {@render children()}
      {/if}
    </div>
  </main>
</div>
