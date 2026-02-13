<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    title?: string;
    class?: string;
    children?: Snippet;
  }

  const { title = 'Split Bill', class: className = '', children }: Props = $props();
</script>

<div class="flex flex-col min-h-screen bg-surface pb-[60px]">
  <!-- Header -->
  <header class="sticky top-0 z-30 bg-white border-b border-surface-200 px-4 py-3">
    <h1 class="text-xl font-semibold text-text">{title}</h1>
  </header>

  <!-- Main Content -->
  <main class="flex-1 px-4 py-4 {className}">
    {#if children}
      {@render children()}
    {:else}
      <slot />
    {/if}
  </main>
</div>
