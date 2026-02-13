<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
    class?: string;
    children?: Snippet;
    onclick?: (event: MouseEvent) => void;
  }

  const {
    variant = 'primary',
    size = 'md',
    disabled = false,
    type = 'button',
    class: className = '',
    children,
    onclick
  }: Props = $props();

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:outline-primary-600',
    secondary: 'bg-surface-200 text-text hover:bg-surface-300 focus-visible:outline-primary-600',
    ghost: 'bg-transparent text-text hover:bg-surface-100 focus-visible:outline-primary-600',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus-visible:outline-red-600',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm min-h-[36px]',
    md: 'px-4 py-2 text-base min-h-[44px]',
    lg: 'px-6 py-3 text-lg min-h-[52px]',
  };
</script>

<button
  {type}
  class="{baseClasses} {variantClasses[variant]} {sizeClasses[size]} {className}"
  {disabled}
  on:click={onclick}
>
  {#if children}
    {@render children()}
  {:else}
    <slot />
  {/if}
</button>
