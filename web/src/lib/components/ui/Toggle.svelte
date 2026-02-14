<script lang="ts">
  interface Props {
    checked: boolean;
    onToggle: (checked: boolean) => void;
    label?: string;
    disabled?: boolean;
    class?: string;
  }

  const { checked, onToggle, label, disabled = false, class: className = '' }: Props = $props();

  function handleClick() {
    if (!disabled) {
      onToggle(!checked);
    }
  }
</script>

<label class="inline-flex items-center cursor-pointer {disabled ? 'opacity-50 cursor-not-allowed' : ''} {className}">
  <div class="relative inline-flex items-center h-6 w-11 rounded-full bg-slate-200 transition-colors" class:bg-primary-500={checked}>
    <input
      type="checkbox"
      {checked}
      onchange={() => onToggle(!checked)}
      {disabled}
      class="sr-only peer"
    />
    <div
      class="inline-block h-5 w-5 rounded-full bg-white shadow transition-transform"
      class:translate-x-6={checked}
      class:translate-x-1={!checked}
    />
  </div>
  {#if label}
    <span class="ml-3 text-sm font-medium">{label}</span>
  {/if}
</label>
