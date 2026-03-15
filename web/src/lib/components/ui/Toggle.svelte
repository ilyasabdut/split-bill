<script lang="ts">
  import { cn } from '$lib/utils';

  interface Props {
    checked: boolean;
    onToggle: (checked: boolean) => void;
    label?: string;
    disabled?: boolean;
    class?: string;
    ariaLabel?: string;
    ariaLabelledby?: string;
  }

  const {
    checked,
    onToggle,
    label,
    disabled = false,
    class: className = '',
    ariaLabel,
    ariaLabelledby
  }: Props = $props();

  function handleClick() {
    if (!disabled) {
      onToggle(!checked);
    }
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (disabled) return;

    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      onToggle(!checked);
    }
  }
</script>

<div
  class={cn('inline-flex items-center cursor-pointer', disabled && 'opacity-50 cursor-not-allowed', className)}
  onclick={handleClick}
  onkeydown={handleKeyDown}
  role="switch"
  tabindex="0"
  aria-checked={checked}
  aria-disabled={disabled}
  aria-label={ariaLabel}
  aria-labelledby={ariaLabelledby}
>
  <div class="relative inline-flex items-center h-6 w-11 rounded-full bg-surface-200 transition-colors" class:bg-primary-500={checked}>
    <input
      type="checkbox"
      {checked}
      onchange={() => onToggle(!checked)}
      {disabled}
      class="sr-only"
    />
    <div
      class="inline-block h-5 w-5 rounded-full bg-surface-0 shadow transition-transform"
      class:translate-x-6={checked}
      class:translate-x-1={!checked}
    />
  </div>
  {#if label}
    <span class="ml-3 text-label font-medium text-text-primary">{label}</span>
  {/if}
</div>
