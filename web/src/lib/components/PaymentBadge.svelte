<script lang="ts">
  import { cn } from '$lib/utils';

  interface Props {
    status: 'pending' | 'paid' | 'failed' | 'processing';
    size?: 'sm' | 'md' | 'lg';
    showText?: boolean;
    class?: string;
    ariaLabel?: string;
  }

  const {
    status,
    size = 'md',
    showText = true,
    class: className = '',
    ariaLabel
  }: Props = $props();

  const statusConfig = {
    pending: {
      text: 'Pending',
      color: 'text-yellow-700',
      bgColor: 'bg-yellow-100',
      borderColor: 'border-yellow-200',
      icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    paid: {
      text: 'Paid',
      color: 'text-green-700',
      bgColor: 'bg-green-100',
      borderColor: 'border-green-200',
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    failed: {
      text: 'Failed',
      color: 'text-red-700',
      bgColor: 'bg-red-100',
      borderColor: 'border-red-200',
      icon: 'M10 14l2-2m0 0l2-2m2 2l2 2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    processing: {
      text: 'Processing',
      color: 'text-blue-700',
      bgColor: 'bg-blue-100',
      borderColor: 'border-blue-200',
      icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
    }
  };

  const config = $derived(statusConfig[status]);

  const sizeClasses = {
    sm: {
      container: 'px-2 py-1',
      icon: 'size-3',
      text: 'text-xs'
    },
    md: {
      container: 'px-2.5 py-1.5',
      icon: 'size-4',
      text: 'text-sm'
    },
    lg: {
      container: 'px-3 py-2',
      icon: 'size-5',
      text: 'text-base'
    }
  };

  const sizeConfig = $derived(sizeClasses[size]);
</script>

<div
  class={cn(
    'inline-flex items-center gap-1.5 rounded-full border min-h-[44px]',
    config.bgColor,
    config.borderColor,
    sizeConfig.container,
    className
  )}
  aria-label={ariaLabel || `${config.text} payment status`}
>
  <svg class={cn(config.color, sizeConfig.icon)} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={config.icon} />
  </svg>
  {#if showText}
    <span class={cn(config.color, sizeConfig.text, 'font-medium text-balance')}>
      {config.text}
    </span>
  {/if}
</div>
