# Layout Components

Shared layout components for Split Bill.

## AppShell
```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    title?: string;
    class?: string;
    children?: Snippet;
  }

  const { title = 'Split Bill', class: className = '', children }: Props = $props();
</script>

<div class="flex flex-col min-h-screen bg-surface pb-[60px]">
  <!-- Header -->
  <header class="sticky top-0 z-30 bg-white border-b border-surface-200 px-4 py-3">
    <h1 class="text-xl font-semibold text-text">{title}</h1>
  </header>

  <!-- Main Content -->
  <main class="flex-1 px-4 py-4 {className}">
    {#if children}
      {@render children()}
    {/if}
  </main>
</div>
```

## BottomNav
```svelte
<script lang="ts">
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
  class="fixed bottom-0 left-0 right-0 bg-white border-t border-surface-200 z-40 bottom-nav-safe {className}"
  aria-label="Main navigation"
>
  <ul class="flex items-center justify-around">
    {#each navItems as item}
      <li>
        <a
          href={item.path}
          class="flex flex-col items-center justify-center flex-1 min-h-[60px] text-center transition-colors {currentPath === item.path ? 'text-primary-600' : 'text-text-secondary hover:text-primary-600'}"
          aria-current={currentPath === item.path ? 'page' : undefined}
        >
          <span class="text-2xl mb-1" aria-hidden="true">{item.icon}</span>
          <span class="text-xs font-medium">{item.label}</span>
        </a>
      </li>
    {/each}
  </ul>
</nav>
```

## OfflineBanner
```svelte
<script lang="ts">
  import { offlineStore, isOffline, hasQueuedActions } from '$lib/stores/offline';
</script>

{#if $isOffline}
<div class="fixed top-0 left-0 right-0 z-50 bg-yellow-100 text-yellow-800 px-4 py-3 flex items-center gap-3 shadow-md" role="alert">
  <span class="text-xl" aria-hidden="true">📡</span>
  <span class="flex-1 text-sm font-medium">
    You're offline. Actions will be synced when connection returns.
  </span>
  {#if $hasQueuedActions}
    <span class="px-2 py-1 bg-red-600 text-white text-xs font-semibold rounded-full">
      {$offlineStore.queuedActions} pending
    </span>
  {/if}
</div>
{/if}
```
