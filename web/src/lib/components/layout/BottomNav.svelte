<script lang="ts">
  import { cn } from '$lib/utils';

  interface NavItem {
    path: string;
    icon: string;
    label: string;
  }

  interface Props {
    currentPath: string;
    class?: string;
  }

  const { currentPath, class: className = '' }: Props = $props();

  const navItems: NavItem[] = [
    { path: '/', icon: '🏠', label: 'Home' },
    { path: '/receipt', icon: '📸', label: 'Receipt' },
    { path: '/split', icon: '💰', label: 'Split' },
    { path: '/history', icon: '📋', label: 'History' },
    { path: '/settings', icon: '⚙️', label: 'Settings' },
  ];
</script>

<nav
  class={cn('fixed bottom-0 left-0 right-0 bg-white border-t border-surface-200 z-bottom-nav bottom-nav-safe', className)}
  aria-label="Main navigation"
>
  <ul class="flex items-center justify-around">
    {#each navItems as item}
      <li>
        <a
          href={item.path}
          class={cn('flex flex-col items-center justify-center flex-1 min-h-[60px] text-center transition-colors',
            currentPath === item.path ? 'text-primary-600' : 'text-text-secondary hover:text-primary-600')}
          aria-current={currentPath === item.path ? 'page' : undefined}
        >
          <span class="text-2xl mb-1" aria-hidden="true">{item.icon}</span>
          <span class="text-xs font-medium">{item.label}</span>
        </a>
      </li>
    {/each}
  </ul>
</nav>
