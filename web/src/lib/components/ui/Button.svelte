<script lang="ts">
  interface Props {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
    class?: string;
    onclick?: (event: MouseEvent) => void;
  }

  const {
    variant = 'primary',
    size = 'md',
    disabled = false,
    type = 'button',
    class: className = '',
    onclick
  }: Props = $props();

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-[--color-primary-600] text-white hover:bg-[--color-primary-700]',
    secondary: 'bg-surface-200 text-text hover:bg-surface-300',
    ghost: 'bg-transparent text-text hover:bg-surface-100',
    danger: 'bg-red-600 text-white hover:bg-red-700',
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
  <slot />
</button>
