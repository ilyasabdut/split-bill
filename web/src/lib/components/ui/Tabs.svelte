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
					class="shrink-0 h-[38px] px-5 rounded-full flex items-center justify-center text-[14px] font-semibold transition-all active:scale-95"
					class:bg-slate-900={activeTab === tab.id}
					class:text-white={activeTab === tab.id}
					class:shadow-md={activeTab === tab.id}
					class:shadow-slate-900={activeTab === tab.id && activeTab === tab.id}
					class:bg-white={activeTab !== tab.id}
					class:border={activeTab !== tab.id}
					class:border-slate-200={activeTab !== tab.id}
					class:text-slate-600={activeTab !== tab.id}
					class:active:bg-slate-50={activeTab !== tab.id}
					onclick={(e) => {
						if (tab.href?.startsWith('#')) {
							e.preventDefault();
							setActiveTab(tab.id);
						}
					}}
				>
					{tab.label}
				</a>
			{:else}
				<button
					class="shrink-0 h-[38px] px-5 rounded-full flex items-center justify-center text-[14px] font-semibold transition-all active:scale-95"
					class:bg-slate-900={activeTab === tab.id}
					class:text-white={activeTab === tab.id}
					class:shadow-md={activeTab === tab.id}
					class:shadow-slate-900={activeTab === tab.id && activeTab === tab.id}
					class:bg-white={activeTab !== tab.id}
					class:border={activeTab !== tab.id}
					class:border-slate-200={activeTab !== tab.id}
					class:text-slate-600={activeTab !== tab.id}
					class:active:bg-slate-50={activeTab !== tab.id}
					onclick={() => setActiveTab(tab.id)}
				>
					{tab.label}
				</button>
			{/if}
		{/each}
	</div>
</div>
