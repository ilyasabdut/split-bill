<script lang="ts">
	import { cn } from '$lib/utils';

	interface NavItem {
		path: string;
		icon: string;
		label: string;
		isProminent?: boolean;
	}

	interface Props {
		currentPath: string;
		class?: string;
	}

	const { currentPath, class: className = '' }: Props = $props();

	// Superdesign spec: 4 items in floating pill layout
	// Order: Home, History, Scan (prominent center), Settings
	const navItems: NavItem[] = [
		{ path: '/', icon: 'home', label: 'Home' },
		{ path: '/history', icon: 'history', label: 'History' },
		{ path: '/receipt', icon: 'scan', label: 'Scan', isProminent: true },
		{ path: '/settings', icon: 'settings', label: 'Settings' }
	];

	function getIcon(name: string): string {
		const icons: Record<string, string> = {
			home: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
			history: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>`,
			scan: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><rect width="10" height="10" x="7" y="7" rx="1"/></svg>`,
			settings: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0-.73 2.73l.08.15a2 2 0 0 1 0 2l-.08.15a2 2 0 0 0 .73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 0 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.08-.14a2 2 0 0 1 0-2l.08-.15a2 2 0 0 0-.73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>`
		};
		return icons[name] || icons.home;
	}

	function isActive(path: string, current: string): boolean {
		if (path === '/') return current === '/';
		return current.startsWith(path);
	}

	// Superdesign spec: prominent button (Scan) gets brand background when active
	function isProminentActive(item: NavItem): boolean {
		return !!(item.isProminent && isActive(item.path, currentPath));
	}
</script>

<footer
	class={cn(
		'fixed bottom-0 left-0 right-0 p-4 z-40 pb-safe',
		className
	)}
	aria-label="Main navigation"
>
	<nav
		class="bg-surface-0 border border-surface-200 shadow-elevated rounded-[28px] px-3 py-2 mx-auto max-w-2xl"
	>
		<ul class="grid grid-cols-4 gap-2">
			{#each navItems as item}
				<li>
					<a
						href={item.path}
						class={cn(
							// Base styles matching Superdesign
							'min-h-[44px] flex flex-col items-center justify-center gap-1 py-2 rounded-2xl active:scale-[0.99] transition-all',
							// Regular items (Home, History, Settings)
							!item.isProminent && isActive(item.path, currentPath)
								? 'bg-primary-50 text-primary-600'
								: !item.isProminent
									? 'text-text-tertiary hover:text-primary-600'
									: null,
							// Prominent center button (Scan)
							item.isProminent && isProminentActive(item)
								? 'bg-primary-500 text-text-inverted shadow-md'
								: item.isProminent
									? 'text-text-tertiary'
									: null
						)}
						aria-current={isActive(item.path, currentPath) ? 'page' : undefined}
					>
						{#if item.isProminent}
							<!-- Prominent Scan button: icon in rounded square -->
							<span class="h-11 w-11 rounded-2xl bg-primary-500 shadow-md flex items-center justify-center {isProminentActive(item) ? '' : 'text-white'}">
								<span class="text-white text-2xl" aria-hidden="true">{@html getIcon(item.icon)}</span>
							</span>
						{:else}
							<!-- Regular items: icon + label -->
							<span class="text-xl" aria-hidden="true">{@html getIcon(item.icon)}</span>
						{/if}
						<span class="text-[12px] font-semibold">{item.label}</span>
					</a>
				</li>
			{/each}
		</ul>
	</nav>
</footer>
