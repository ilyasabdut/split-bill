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

  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
</script>

<div
  class={cn('bg-surface-0 rounded-xl shadow-card border border-surface-200', paddingClasses[padding], className)}
  {onclick}
>
  {#if children}
    {@render children()}
  {/if}
</div>
