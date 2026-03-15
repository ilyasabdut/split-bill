<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';

	interface Tab {
		id: string;
		label: string;
		href?: string;
		active?: boolean;
	}

	interface Props extends HTMLAttributes<HTMLDivElement> {
		tabs: Tab[];
		class?: string;
	}

	let { tabs, class: className = '', ...restProps }: Props = $props();

	let activeTab = $state(tabs.find((t) => t.active)?.id || tabs[0]?.id);

	function setActiveTab(id: string) {
		activeTab = id;
	}
</script>

<div class="-mx-4 overflow-hidden" {...restProps}>
	<div
		class="flex items-center gap-2 overflow-x-auto px-4 pb-2 no-scrollbar scroll-smooth"
		class:className
	>
		{#each tabs as tab (tab.id)}
			{#if tab.href}
				<a
					href={tab.href}
					class="shrink-0 h-[38px] px-5 rounded-full flex items-center justify-center text-label font-semibold transition-all active:scale-95 max-w-[180px]"
					class:bg-primary-500={activeTab === tab.id}
					class:text-text-inverted={activeTab === tab.id}
					class:shadow-md={activeTab === tab.id}
					class:bg-surface-0={activeTab !== tab.id}
					class:border={activeTab !== tab.id}
					class:border-surface-200={activeTab !== tab.id}
					class:text-text-secondary={activeTab !== tab.id}
					class:active:bg-surface-50={activeTab !== tab.id}
					onclick={(e) => {
						if (tab.href?.startsWith('#')) {
							e.preventDefault();
							setActiveTab(tab.id);
						}
					}}
				>
					<span class="truncate">{tab.label}</span>
				</a>
			{:else}
				<button
					class="shrink-0 h-[38px] px-5 rounded-full flex items-center justify-center text-label font-semibold transition-all active:scale-95 max-w-[180px]"
					class:bg-primary-500={activeTab === tab.id}
					class:text-text-inverted={activeTab === tab.id}
					class:shadow-md={activeTab === tab.id}
					class:bg-surface-0={activeTab !== tab.id}
					class:border={activeTab !== tab.id}
					class:border-surface-200={activeTab !== tab.id}
					class:text-text-secondary={activeTab !== tab.id}
					class:active:bg-surface-50={activeTab !== tab.id}
					onclick={() => setActiveTab(tab.id)}
				>
					<span class="truncate">{tab.label}</span>
				</button>
			{/if}
		{/each}
	</div>
</div>
