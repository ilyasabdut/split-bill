<script lang="ts">
  interface Props {
    padding?: 'none' | 'sm' | 'md' | 'lg';
    class?: string;
  }

  const { padding = 'md', class: className = '' }: Props = $props();

  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
</script>

<div class="bg-white rounded-xl shadow-sm border border-surface-200 {paddingClasses[padding]} {className}">
  <slot />
</div>
