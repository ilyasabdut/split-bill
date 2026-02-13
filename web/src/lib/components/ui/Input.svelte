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
  }: Props = $props();
</script>

<div class="relative">
  <input
    {type}
    {placeholder}
    {disabled}
    {required}
    bind:value={value}
    oninput={(e) => {
      if (oninput) oninput(e.currentTarget.value);
      if (onchange) onchange(e.currentTarget.value);
    }}
    onkeydown={onkeydown}
    class="w-full px-4 py-3 text-base bg-white border border-surface-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none disabled:bg-surface-100 disabled:cursor-not-allowed min-h-[44px] {className}"
  />
</div>
