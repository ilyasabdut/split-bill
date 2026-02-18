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
    { path: '/', icon: 'home', label: 'Home' },
    { path: '/receipt', icon: 'scan', label: 'Scan' },
    { path: '/split', icon: 'split', label: 'Split' },
    { path: '/history', icon: 'history', label: 'History' },
    { path: '/settings', icon: 'settings', label: 'Settings' },
  ];

  function getIcon(name: string): string {
    const icons: Record<string, string> = {
      home: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
      scan: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><rect width="10" height="10" x="7" y="7" rx="1"/></svg>`,
      split: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>`,
      history: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>`,
      settings: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0-.73 2.73l.08.15a2 2 0 0 1 0 2l-.08.15a2 2 0 0 0 .73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 0 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.08-.14a2 2 0 0 1 0-2l.08-.15a2 2 0 0 0-.73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>`,
    };
    return icons[name] || icons.home;
  }

  function isActive(path: string, current: string): boolean {
    if (path === '/') return current === '/';
    return current.startsWith(path);
  }
</script>

<nav
  class={cn(
    'fixed bottom-0 left-0 right-0 bg-white border-t border-surface-200 z-bottom-nav w-full max-w-full',
    className
  )}
  style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 0.5rem);"
  aria-label="Main navigation"
>
  <ul class="flex items-center justify-around max-w-lg mx-auto">
    {#each navItems as item}
      <li>
        <a
          href={item.path}
          class={cn(
            'flex flex-col items-center justify-center min-h-[60px] min-w-[44px] px-2 text-center transition-colors',
            isActive(item.path, currentPath)
              ? 'text-primary-600'
              : 'text-text-secondary hover:text-primary-600 active:scale-95'
          )}
          aria-current={isActive(item.path, currentPath) ? 'page' : undefined}
        >
          <span class="text-lg mb-1" aria-hidden="true">{@html getIcon(item.icon)}</span>
          <span class="text-xs font-medium">{item.label}</span>
        </a>
      </li>
    {/each}
  </ul>
</nav>
