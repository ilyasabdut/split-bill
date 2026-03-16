<script lang="ts">
  import type { Snippet } from 'svelte';
  import { cn } from '$lib/utils';

  interface Props {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
    class?: string;
    children?: Snippet;
    onclick?: (event: MouseEvent) => void;
    ariaLabel?: string;  // Note: Use aria-label prop in template, not ariaLabel
    ariaLabelledby?: string;
    ariaControls?: string;
    ariaExpanded?: boolean;
  }

  const {
    variant = 'primary',
    size = 'md',
    disabled = false,
    type = 'button',
    class: className = '',
    children,
    onclick,
    ariaLabel,
    ariaLabelledby,
    ariaControls,
    ariaExpanded
  }: Props = $props();

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-w-0';

  const variantClasses = {
    primary: 'bg-primary-500 text-text-inverted hover:bg-primary-600',
    secondary: 'bg-surface-100 text-text-primary hover:bg-surface-200 border border-surface-200',
    ghost: 'bg-transparent text-text-primary hover:bg-surface-50',
    danger: 'bg-error text-text-inverted hover:bg-error/90',
    outline: 'bg-transparent border-2 border-surface-200 text-text-primary hover:bg-surface-50 hover:border-surface-300',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-label min-h-[44px]',
    md: 'px-4 py-2 text-body min-h-[44px]',
    lg: 'px-6 py-3 text-subheading min-h-[52px]',
  };
</script>

<button
  {type}
  class={cn(baseClasses, variantClasses[variant], sizeClasses[size], 'max-w-full', className)}
  {disabled}
  {onclick}
  aria-label={ariaLabel}
  aria-labelledby={ariaLabelledby}
  aria-controls={ariaControls}
  aria-expanded={ariaExpanded}
>
  {#if children}
    <span class="truncate max-w-full">{@render children()}</span>
  {/if}
</button>
