<script lang="ts">
	import { onMount } from 'svelte';
	import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';
	import { currencyStore, analyticsStore } from '$lib/stores';
	import type { SplitResults } from '$lib/types/split';
	import LoadingSpinner from '$lib/components/ui/LoadingSpinner.svelte';
	import SkeletonLoader from '$lib/components/ui/SkeletonLoader.svelte';

	interface HistoryItem {
		id: string;
		createdAt: number;
		people: string[];
		total: number;
		results: SplitResults;
		currency?: string;
		group?: string;
		status?: 'unpaid' | 'completed';
		title?: string;
		category?: string;
	}

	let history = $state<HistoryItem[]>([]);
	let loading = $state(true);
	let monthlySpending = $state<number>(4250000);
	let peopleCount = $state<number>(12);
	let pendingCount = $state<number>(2);
	let youOwe = $state<number>(150000);
	let owedToYou = $state<number>(320000);

	onMount(async () => {
		try {
			await Promise.all([
				currencyStore.init(),
				analyticsStore.loadAnalytics()
			]);

			const indexedDB = await getIndexedDB();
			const items = await indexedDB.getAll<any>(STORES.SPLITS);

			history = items
				.filter(item => item.createdAt)
				.sort((a, b) => b.createdAt - a.createdAt)
				.map(item => {
					const people = Object.keys(item.results || {});
					return {
						id: String(item.id),
						createdAt: Number(item.createdAt),
						people,
						total: Number(Object.values(item.results || {}).reduce((sum: number, person: any) => sum + person.total, 0)),
						results: item.results,
						currency: String(item.currency || 'IDR'),
						group: String(item.group || ''),
						status: item.status || 'unpaid',
						title: people.length > 0 ? people.join(', ') : 'Untitled Split',
						category: 'food'
					};
				}) as HistoryItem[];

			peopleCount = new Set(history.flatMap(item => item.people)).size;
			pendingCount = history.filter(item => item.status === 'unpaid').length;
		} catch (error) {
			console.error('Failed to load history:', error);
		} finally {
			loading = false;
		}
	});

	function formatDate(timestamp: number): string {
		const date = new Date(timestamp);
		const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
		return `${months[date.getMonth()]} ${date.getDate()}, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
	}

	function formatAmount(amount: number): string {
		if (amount >= 1000000) {
			return `IDR ${(amount / 1000000).toFixed(1)}M`;
		} else if (amount >= 1000) {
			return `IDR ${(amount / 1000).toFixed(0)}k`;
		}
		return `IDR ${amount.toLocaleString('id-ID')}`;
	}

	function getIconForCategory(category: string): string {
		if (category === 'food' || category === 'sushi') {
			return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>`;
		}
		return `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>`;
	}
</script>

<svelte:head>
	<title>History - Split Bill</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
</svelte:head>

<div class="w-full h-screen flex flex-col bg-surface-50 dark:bg-surface-900 text-text-primary dark:text-text-primary font-sans">
	<!-- Header -->
	<header class="shrink-0 pt-12 px-4 pb-2 bg-surface-0 dark:bg-surface-800 border-b border-surface-100 dark:border-surface-700 sticky top-0 z-30">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="w-11 h-11 rounded-2xl bg-primary-100/50 dark:bg-primary-900/30 shadow-sm flex items-center justify-center">
					<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-600 dark:text-primary-400"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
				</div>
				<div>
					<h1 class="text-subheading leading-tight font-bold tracking-tight">History</h1>
					<p class="text-caption text-text-tertiary font-medium">Recent splits & settlements</p>
				</div>
			</div>
			<a href="#search" class="w-11 h-11 rounded-2xl bg-surface-0 dark:bg-surface-700 shadow-sm border border-surface-200 dark:border-surface-600 flex items-center justify-center text-text-secondary dark:text-text-tertiary active:scale-95 transition-transform hover:bg-surface-50 dark:hover:bg-surface-600" aria-label="Search splits">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
			</a>
		</div>

		<!-- Scrollable Tabs -->
		<nav class="mt-5 -mx-4 overflow-hidden">
			<div class="flex items-center gap-2 overflow-x-auto px-4 pb-2 no-scrollbar scroll-smooth">
				<a href="#all" class="shrink-0 h-11 px-5 rounded-full flex items-center justify-center text-label font-semibold bg-text-primary dark:bg-surface-0 text-text-inverted dark:text-text-primary shadow-md shadow-text-primary/10">All</a>
				<a href="#unpaid" class="shrink-0 h-11 px-5 rounded-full flex items-center justify-center text-label font-semibold bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-secondary dark:text-text-tertiary active:bg-surface-50 dark:active:bg-surface-600">Unpaid</a>
				<a href="#completed" class="shrink-0 h-11 px-5 rounded-full flex items-center justify-center text-label font-semibold bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-secondary dark:text-text-tertiary active:bg-surface-50 dark:active:bg-surface-600">Completed</a>
				<a href="#groups" class="shrink-0 h-11 px-5 rounded-full flex items-center justify-center text-label font-semibold bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-secondary dark:text-text-tertiary active:bg-surface-50 dark:active:bg-surface-600">Groups</a>
				<a href="#templates" class="shrink-0 h-11 px-5 rounded-full flex items-center justify-center text-label font-semibold bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-secondary dark:text-text-tertiary active:bg-surface-50 dark:active:bg-surface-600">Templates</a>
				<a href="#analytics" class="shrink-0 h-11 px-5 rounded-full flex items-center justify-center text-label font-semibold bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-secondary dark:text-text-tertiary active:bg-surface-50 dark:active:bg-surface-600">Analytics</a>
			</div>
		</nav>
	</header>

	<!-- Main content (scrollable) -->
	<main class="flex-1 overflow-y-auto px-4 pb-[120px] pt-2">
		{#if loading}
			<LoadingSpinner text="Loading history..." />
			<SkeletonLoader count={5} />
		{:else}
			<!-- Currency Selector -->
			<div class="flex justify-center mb-4">
				<button class="flex items-center gap-2 px-4 py-1.5 bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 rounded-full shadow-sm text-sm font-semibold text-text-primary dark:text-text-primary active:scale-95 transition-transform">
					<span class="w-5 h-5 rounded-full bg-surface-100 dark:bg-surface-600 flex items-center justify-center text-[10px]">🇮🇩</span>
					IDR
					<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="m6 9 6 6 6-6"/></svg>
				</button>
			</div>

			<!-- Monthly Spending Summary -->
			<section class="mb-section relative group animate-fade-in">
				<div class="absolute inset-0 bg-primary-500 rounded-3xl blur-xl opacity-20 group-hover:opacity-30 transition-opacity"></div>
				<div class="relative bg-primary-600 rounded-3xl p-6 text-text-inverted shadow-xl overflow-hidden">
					<!-- Decorative circles -->
					<div class="absolute top-0 right-0 w-32 h-32 bg-surface-0/10 rounded-full -mr-10 -mt-10 blur-2xl"></div>

					<div class="relative z-10">
						<div class="flex justify-between items-start">
							<p class="text-primary-100 text-label font-medium">Total spending this month</p>
							<span class="bg-surface-0/30 px-2.5 py-1 rounded-lg text-caption font-semibold text-text-inverted flex items-center gap-1">
								<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
								12.5%
							</span>
						</div>
						<h2 class="text-heading font-bold tracking-tight mt-2 tabular-ns">IDR 4,250,000</h2>
						<p class="text-caption text-primary-200 mt-1 opacity-80">+IDR 450,000 vs last month</p>
					</div>
				</div>
			</section>

			<!-- Summary Chips -->
			<section class="mb-section overflow-x-auto no-scrollbar animate-slide-up animate-delay-100">
				<div class="flex gap-3 pb-1 min-w-max">
					<div class="bg-surface-0 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 shadow-card rounded-2xl pl-3 pr-4 py-2.5 flex items-center gap-3">
						<span class="w-10 h-10 rounded-xl bg-surface-50 dark:bg-surface-700 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary dark:text-text-tertiary"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
						</span>
						<div>
							<p class="text-caption uppercase tracking-wider text-text-tertiary font-bold leading-tight">People</p>
							<p class="text-label font-bold text-text-primary">{peopleCount} Friends</p>
						</div>
					</div>
					<div class="bg-surface-0 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 shadow-card rounded-2xl pl-3 pr-4 py-2.5 flex items-center gap-3">
						<span class="w-10 h-10 rounded-xl bg-warning/10 dark:bg-warning/20 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-warning"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 12 2"/></svg>
						</span>
						<div>
							<p class="text-caption uppercase tracking-wider text-text-tertiary font-bold leading-tight">Pending</p>
							<p class="text-label font-bold text-text-primary">{pendingCount} Splits</p>
						</div>
					</div>
				</div>
			</section>

			<!-- Settlement Summary -->
			<section class="mb-section animate-slide-up animate-delay-200">
				<h3 class="text-label font-bold text-text-primary mb-3 ml-1 flex items-center gap-2">Settlement Summary</h3>
				<div class="grid grid-cols-2 gap-3">
					<!-- You Owe -->
					<div class="bg-error/10 dark:bg-error/20 border border-error/20 p-4 rounded-2xl active:scale-95 transition-all duration-200 cursor-pointer hover:shadow-md hover:scale-[1.02]">
						<div class="w-10 h-10 rounded-full bg-error/20 dark:bg-error/80 text-error flex items-center justify-center mb-3">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><polyline points="10 14 21 3"/></svg>
						</div>
						<p class="text-caption text-error font-semibold uppercase tracking-wide">You Owe</p>
						<p class="text-subheading font-bold text-error mt-1 tabular-ns">IDR 150k</p>
						<div class="mt-2 flex items-center gap-1.5">
							<div class="w-5 h-5 rounded-full bg-error/30 dark:bg-error/70 border border-surface-0 dark:border-error-90 text-caption flex items-center justify-center font-bold text-error">S</div>
							<p class="text-caption text-error font-medium truncate">to Sarah</p>
						</div>
					</div>

					<!-- Owed to You -->
					<div class="bg-success/10 dark:bg-success/20 border border-success/20 p-4 rounded-2xl active:scale-95 transition-all duration-200 cursor-pointer hover:shadow-md hover:scale-[1.02]">
						<div class="w-10 h-10 rounded-full bg-success/20 dark:bg-success/80 text-success flex items-center justify-center mb-3">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 13v6a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v5"/><polyline points="9 3 3 9 9 15"/></svg>
						</div>
						<p class="text-caption text-success font-semibold uppercase tracking-wide">Owed to You</p>
						<p class="text-subheading font-bold text-success mt-1 tabular-ns">IDR 320k</p>
						<div class="mt-2 flex items-center gap-1.5">
							<div class="w-5 h-5 rounded-full bg-success/30 dark:bg-success/70 border border-surface-0 dark:border-success/90 text-caption flex items-center justify-center font-bold text-success">M</div>
							<p class="text-caption text-success font-medium truncate">from Mike</p>
						</div>
					</div>
				</div>
			</section>

			<!-- Split cards -->
			<section aria-label="Split list">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-subheading font-bold text-text-primary">Recent Activity</h2>
					<a href="#all" class="h-8 px-3 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-700 inline-flex items-center justify-center text-caption font-semibold text-primary-600 transition-colors">View all</a>
				</div>

				<div class="space-y-4">
					{#each history.slice(0, 10) as item, index}
						<a href="/split/{item.id}" class="group block bg-surface-0 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 shadow-card rounded-2xl p-4 active:scale-[0.99] transition-all relative overflow-hidden animate-slide-in-right hover:shadow-elevated" style="animation-delay: {Math.min(index * 50 + 300, 600)}ms;">
							<!-- Status Line Indicator -->
							<div class="absolute left-0 top-0 bottom-0 w-1" class:bg-warning={item.status === 'unpaid'} class:bg-success={item.status === 'completed'}></div>

							<div class="flex items-start gap-4">
								<div class="w-12 h-12 rounded-2xl bg-surface-50 dark:bg-surface-700 border border-surface-100 dark:border-surface-600 flex items-center justify-center shrink-0 group-hover:bg-primary-50 dark:group-hover:bg-primary-900/30 group-hover:border-primary-100 dark:group-hover:border-primary-800 transition-colors">
									{@html getIconForCategory(item.category)}
								</div>
								<div class="flex-1 min-w-0">
									<div class="flex items-start justify-between gap-3">
										<div class="min-w-0">
											<h3 class="text-label font-bold text-text-primary truncate">{item.title}</h3>
											<p class="text-caption text-text-tertiary mt-0.5">{formatDate(item.createdAt)}</p>
										</div>
										<div class="text-right shrink-0">
											<p class="text-subheading font-bold text-text-primary leading-none tabular-ns">{formatAmount(item.total)}</p>
											{#if item.status === 'unpaid'}
												<span class="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-caption font-bold bg-warning/10 text-warning border border-warning/20">
													<span class="w-1.5 h-1.5 rounded-full bg-warning"></span>
													Unpaid
												</span>
											{:else}
												<div class="mt-1.5 flex flex-col items-end">
													<span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-caption font-bold text-success bg-success/10 border border-success/20">
														<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 12 15 15 9"/></svg>
														Completed
													</span>
													<span class="text-caption text-text-tertiary font-medium">Paid on Jan 14</span>
												</div>
											{/if}
										</div>
									</div>

									<div class="mt-3 pt-3 border-t border-surface-100 dark:border-surface-700 flex items-center justify-between">
										<div class="flex items-center gap-2 text-text-tertiary">
											<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
											<span class="text-caption font-medium">{item.people.length} people</span>
										</div>
										<div class="flex -space-x-2">
											{#each item.people.slice(0, 4) as person}
												<div class="w-6 h-6 rounded-full bg-surface-200 dark:bg-surface-600 ring-2 ring-surface-0 dark:ring-surface-800 flex items-center justify-center text-caption font-bold text-text-secondary dark:text-text-tertiary">{person[0]}</div>
											{/each}
										</div>
									</div>
								</div>
							</div>
						</a>
					{/each}
				</div>
			</section>
		{/if}
	</main>
</div>
