<script lang="ts">
  interface Props {
    size?: 'sm' | 'md' | 'lg';
    text?: string;
    fullScreen?: boolean;
  }

  let { size = 'md', text = 'Loading...', fullScreen = false }: Props = $props();

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };
</script>

{#if fullScreen}
  <div class="fixed inset-0 bg-surface-0/80 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="text-center">
      <div class="inline-block animate-spin rounded-full border-4 border-surface-200 border-t-primary-500 {sizeClasses[size]} motion-reduce:animate-[spin_3s_linear_infinite]"></div>
      {#if text}
        <p class="mt-3 text-label text-text-secondary">{text}</p>
      {/if}
    </div>
  </div>
{:else}
  <div class="flex items-center justify-center py-8">
    <div class="text-center">
      <div class="inline-block animate-spin rounded-full border-4 border-surface-200 border-t-primary-500 {sizeClasses[size]} motion-reduce:animate-[spin_3s_linear_infinite]"></div>
      {#if text}
        <p class="mt-3 text-label text-text-secondary">{text}</p>
      {/if}
    </div>
  </div>
{/if}
