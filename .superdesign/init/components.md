# Components

Shared UI primitives and layout components for Split Bill.

## shared/Button.svelte
```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
    class?: string;
    children?: Snippet;
    onclick?: (event: MouseEvent) => void;
  }

  const {
    variant = 'primary',
    size = 'md',
    disabled = false,
    type = 'button',
    class: className = '',
    children,
    onclick
  }: Props = $props();

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-[--color-primary-600] text-white hover:bg-[--color-primary-700]',
    secondary: 'bg-surface-200 text-text hover:bg-surface-300',
    ghost: 'bg-transparent text-text hover:bg-surface-100',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm min-h-[36px]',
    md: 'px-4 py-2 text-base min-h-[44px]',
    lg: 'px-6 py-3 text-lg min-h-[52px]',
  };
</script>

<button
  {type}
  class="{baseClasses} {variantClasses[variant]} {sizeClasses[size]} {className}"
  {disabled}
  {onclick}
>
  {#if children}
    {@render children()}
  {/if}
</button>
```

## shared/Card.svelte
```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    padding?: 'none' | 'sm' | 'md' | 'lg';
    class?: string;
    children?: Snippet;
    onclick?: () => void;
  }

  const { padding = 'md', class: className = '', children, onclick }: Props = $props();

  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
</script>

<div
  class="bg-white rounded-xl shadow-sm border border-surface-200 {paddingClasses[padding]} {className}"
  on:click={onclick}
  on:keydown={(e) => e.key === 'Enter' && onclick?.()}
  role={onclick ? "button" : undefined}
  tabindex={onclick ? 0 : undefined}
>
  {#if children}
    {@render children()}
  {/if}
</div>
```

## shared/Input.svelte
```svelte
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
```

## shared/Progress.svelte
```svelte
<script lang="ts">
  interface Props {
    value: number;
    max?: number;
    class?: string;
  }

  const { value, max = 100, class: className = '' }: Props = $props();

  const percentage = $derived(Math.min(100, Math.max(0, (value / max) * 100)));
</script>

<div class="w-full bg-surface-200 rounded-full overflow-hidden {className}" role="progressbar" aria-valuenow={value} aria-valuemin="0" aria-valuemax={max}>
  <div
    class="h-full bg-[--color-primary-600] transition-all duration-300 ease-out"
    style="width: {percentage}%"
  ></div>
</div>
```

## layout/AppShell.svelte
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
  <header class="sticky top-0 z-30 bg-white border-b border-surface-200 px-4 py-3">
    <h1 class="text-xl font-semibold text-text">{title}</h1>
  </header>

  <main class="flex-1 px-4 py-4 {className}">
    {#if children}
      {@render children()}
    {/if}
  </main>
</div>
```

## layout/BottomNav.svelte
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
