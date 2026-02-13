<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    fallback?: Snippet;
    class?: string;
  }

  const { fallback, class: className = '' }: Props = $props();

  let error = $state<Error | null>(null);

  const handleError = (error: Error) => {
    console.error('Error boundary caught:', error);
  };

  // Reset error when component receives new props
  $effect(() => {
    error = null;
  });
</script>

{#if error}
  <div class="min-h-screen flex items-center justify-center px-4 py-8">
    <div class="text-center">
      <div class="text-6xl mb-4" aria-hidden="true">⚠️</div>
      <h2 class="text-xl font-bold mb-2">Something went wrong</h2>
      <p class="text-text-secondary mb-4">An error occurred while processing your request.</p>
    </div>
  </div>
{:else}
  <div class={className}>
    {#if fallback}
      {@render fallback()}
    {:else}
      <slot />
    {/if}
  </div>
{/if}
