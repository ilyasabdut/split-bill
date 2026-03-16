<script lang="ts">
  import type { Snippet } from 'svelte';
  import { cn } from '$lib/utils';

  interface Props {
    padding?: 'none' | 'sm' | 'md' | 'lg';
    class?: string;
    children?: Snippet;
    onclick?: (event: MouseEvent) => void;
  }

  const { padding = 'md', class: className = '', children, onclick }: Props = $props();

  const isInteractive = !!onclick;

  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  function handleClick(e: MouseEvent) {
    if (onclick) {
      onclick(e);
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (isInteractive && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      handleClick(e as unknown as MouseEvent);
    }
  }
</script>

<div
  class={cn('bg-surface-0 rounded-xl shadow-card border border-surface-200', paddingClasses[padding], isInteractive ? 'cursor-pointer' : '', className)}
  onclick={handleClick}
  onkeydown={handleKeydown}
  role={isInteractive ? 'button' : undefined}
  tabindex={isInteractive ? 0 : undefined}
>
  {#if children}
    {@render children()}
  {/if}
</div>
