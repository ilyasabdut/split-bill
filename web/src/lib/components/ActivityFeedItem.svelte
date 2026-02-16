<script lang="ts">
  export interface Activity {
    id: string;
    type: 'split_created' | 'payment_made' | 'member_joined' | 'member_left' | 'template_used' | 'split_completed';
    user: {
      id: number;
      name: string;
      avatar_url?: string;
    };
    data: Record<string, any>;
    created_at: string;
  }

  interface Props {
    activity: Activity;
    class?: string;
  }

  const { activity, class: className = '' }: Props = $props();

  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'split_created':
        return 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z';
      case 'payment_made':
        return 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z';
      case 'member_joined':
        return 'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z';
      case 'member_left':
        return 'M13 7a4 4 0 11-8 0 4 4 0 018 0zM9 14a6 6 0 00-6 6v1h12v-1a6 6 0 00-6-6zM21 12h-3m-3 0h-3m-3 0h-3';
      case 'template_used':
        return 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z';
      case 'split_completed':
        return 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z';
      default:
        return 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z';
    }
  };

  const getActivityMessage = (activity: Activity) => {
    const { type, user, data } = activity;

    switch (type) {
      case 'split_created':
        return `${user.name} created a new split: "${data.split_name}"`;
      case 'payment_made':
        return `${user.name} made a payment of ${data.amount} ${data.currency}`;
      case 'member_joined':
        return `${user.name} joined the group "${data.group_name}"`;
      case 'member_left':
        return `${user.name} left the group "${data.group_name}"`;
      case 'template_used':
        return `${user.name} used template "${data.template_name}"`;
      case 'split_completed':
        return `Split "${data.split_name}" has been completed`;
      default:
        return `${user.name} performed an action`;
    }
  };

  const getActivityTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };
</script>

<div class={cn('flex items-start gap-3 p-3 hover:bg-surface-50 rounded-lg transition-colors', className)}>
  <!-- Icon -->
  <div class="flex-shrink-0 size-10 rounded-full bg-primary-100 flex items-center justify-center">
    <svg class="size-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getActivityIcon(activity.type)} />
    </svg>
  </div>

  <!-- Content -->
  <div class="flex-1 min-w-0">
    <div class="flex items-start justify-between gap-2">
      <p class="text-sm text-text text-balance">
        {getActivityMessage(activity)}
      </p>
      <span class="text-xs text-text-secondary whitespace-nowrap tabular-nums">
        {getActivityTime(activity.created_at)}
      </span>
    </div>

    <!-- Additional details if available -->
    {#if activity.data.description}
      <p class="text-xs text-text-secondary mt-1 text-balance">
        {activity.data.description}
      </p>
    {/if}
  </div>
</div>
