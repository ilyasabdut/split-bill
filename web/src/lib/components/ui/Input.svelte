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
  }

  const {
    type = 'text',
    value = '',
    placeholder = '',
    disabled = false,
    required = false,
    class: className = '',
    oninput,
    onchange,
  }: Props = $props();

  let inputValue = $state(value);

  $effect(() => {
    inputValue = value;
  });
</script>

<div class="relative">
  <input
    {type}
    {placeholder}
    {disabled}
    {required}
    bind:value={inputValue}
    oninput={(e) => {
      if (oninput) oninput(e.currentTarget.value);
      if (onchange) onchange(e.currentTarget.value);
    }}
    class="w-full px-4 py-3 text-base bg-white border border-surface-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none disabled:bg-surface-100 disabled:cursor-not-allowed min-h-[44px] {className}"
  />
</div>
