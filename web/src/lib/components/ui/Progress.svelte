<script lang="ts">
  interface Props {
    value: number;
    max?: number;
    class?: string;
  }

  const { value, max = 100, class: className = '' }: Props = $props();

  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
</script>

<div class="w-full bg-surface-200 rounded-full overflow-hidden {className}" role="progressbar" aria-valuenow={value} aria-valuemin="0" aria-valuemax={max}>
  <div
    class="h-full bg-[--color-primary-600] transition-all duration-300 ease-out"
    style="width: {percentage}%"
  />
</div>
