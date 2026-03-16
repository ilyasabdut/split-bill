<script lang="ts">
  interface Props {
    type?: 'text' | 'email' | 'tel' | 'number';
    value?: string;
    placeholder?: string;
    disabled?: boolean;
    required?: boolean;
    class?: string;
    oninput?: (value: string) => void;
    onchange?: (value: string) => void;
    onkeydown?: (event: KeyboardEvent) => void;
    maxLength?: number;
    min?: number;
    max?: number;
    pattern?: string;
    error?: string;
  }

  let {
    type = 'text',
    value = $bindable(''),
    placeholder = '',
    disabled = false,
    required = false,
    class: className = '',
    oninput,
    onchange,
    onkeydown,
    maxLength,
    min,
    max,
    pattern,
    error = '',
  }: Props = $props();

  let inputElement = $state<HTMLInputElement>();

  function validateInput(e: Event) {
    const target = e.target as HTMLInputElement;

    // For number inputs, ensure positive values
    if (type === 'number' && target.value) {
      const numValue = parseFloat(target.value);
      if (numValue < 0) {
        target.value = '0';
        value = '0';
      }
      if (min !== undefined && numValue < min) {
        target.value = String(min);
        value = String(min);
      }
      if (max !== undefined && numValue > max) {
        target.value = String(max);
        value = String(max);
      }
    }

    // For text inputs, enforce max length
    if (maxLength && target.value.length > maxLength) {
      target.value = target.value.slice(0, maxLength);
      value = target.value;
    }

    if (oninput) oninput(target.value);
    if (onchange) onchange(target.value);
  }
</script>

<div class="relative">
  <input
    {type}
    {placeholder}
    {disabled}
    {required}
    maxlength={maxLength}
    {min}
    {max}
    {pattern}
    bind:value={value}
    bind:this={inputElement}
    oninput={validateInput}
    onkeydown={onkeydown}
    class="w-full px-4 py-3 text-base bg-surface-0 border border-surface-200 rounded-lg focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 focus-visible:outline-none disabled:bg-surface-50 disabled:cursor-not-allowed min-h-[44px] text-text-primary placeholder:text-text-tertiary {className} {error ? 'border-error text-error focus:ring-error/20' : ''}"
  />
  {#if error}
    <p class="mt-1 text-sm text-error">{error}</p>
  {/if}
</div>
