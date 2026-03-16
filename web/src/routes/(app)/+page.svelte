<script lang="ts">
	import { onMount } from 'svelte';
	import { currencyStore, analyticsStore } from '$lib/stores';
	import { goto } from '$app/navigation';
	import CurrencyConverter from '$lib/components/ui/CurrencyConverter.svelte';

	let monthlySpending = $state(3850000);
	let settledCount = $state(5);
	let totalCount = $state(7);
	let pendingCount = $state(2);
	let showCurrencyConverter = $state(false);

	const groups = [
		{ id: 'roomies', name: 'Roomies', icon: 'sofa', color: 'violet', members: 4, lastActivity: '2d ago' },
		{ id: 'gamecrew', name: 'Game Crew', icon: 'gamepad-2', color: 'pink', members: 6, lastActivity: 'Yesterday' },
		{ id: 'hikers', name: 'Hikers', icon: 'mountain', color: 'emerald', members: 12, lastActivity: '1w ago' },
	];

	const activities = [
		{ person: 'Maya', personColor: 'sky', action: 'marked', target: 'Sushi Night', type: 'paid', time: '2h' },
		{ person: 'Jordan', personColor: 'emerald', action: 'joined', target: 'Road Trip', type: 'split', time: '5h' },
	];

	const recentSplits = [
		{ id: '1', title: 'Sushi Night', date: 'Feb 9', people: 4, amount: 'Rp 1.350k', status: 'Unpaid', icon: 'utensils', color: 'primary' },
		{ id: '2', title: 'Road Trip Gas', date: 'Feb 6', people: 3, amount: 'Rp 815k', status: 'Paid', icon: 'car', color: 'emerald' },
		{ id: '3', title: 'Movie Snacks', date: 'Feb 2', people: 2, amount: 'Rp 295k', status: 'Unpaid', icon: 'popcorn', color: 'amber' },
	];

	const templates = [
		{ id: 'lunch', name: 'Lunch', count: 3, icon: 'utensils', color: 'orange' },
		{ id: 'rent', name: 'Rent', count: 0, icon: 'home', color: 'emerald' },
		{ id: 'trip', name: 'Trip', count: 0, icon: 'plane', color: 'sky' },
	];

	onMount(async () => {
		await Promise.all([
			currencyStore.init(),
			analyticsStore.loadAnalytics()
		]);
	});

	// Color utility to return complete Tailwind class strings using semantic tokens
	function getColorClasses(color: string, type: 'bg' | 'text' | 'border'): string {
		const colorMap: Record<string, { bg: string, text: string, border: string }> = {
			orange: { bg: 'bg-orange-50', text: 'text-orange-500', border: 'border-orange-100' },
			emerald: { bg: 'bg-success/10', text: 'text-success', border: 'border-success/20' },
			sky: { bg: 'bg-info/10', text: 'text-info', border: 'border-info/20' },
			violet: { bg: 'bg-violet-100', text: 'text-violet-600', border: 'border-violet-200' },
			pink: { bg: 'bg-pink-100', text: 'text-pink-600', border: 'border-pink-200' },
			primary: { bg: 'bg-primary-50', text: 'text-primary-600', border: 'border-primary-500/15' },
			amber: { bg: 'bg-warning/10', text: 'text-warning', border: 'border-warning/20' },
		};
		return colorMap[color]?.[type] || colorMap.primary[type];
	}

	// Get status color classes using semantic tokens
	function getStatusClasses(status: string): { bg: string, text: string } {
		return status === 'Paid'
			? { bg: 'bg-success/10', text: 'text-success' }
			: { bg: 'bg-warning/10', text: 'text-warning' };
	}

	function getIcon(name: string): string {
		const icons: Record<string, string> = {
			utensils: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>`,
			home: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
			plane: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h20"/><path d="M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-6"/><path d="M12 2 2 7l10 5 2-9Z"/></svg>`,
			car: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>`,
			popcorn: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 12c1-1 3.3-2 5-2 2.7 0 4 2 4 2s1.3-2 4-2c1.7 0 3 1 5 2"/><path d="M12 13c-1 1-3.3 2-5 2-2.7 0-4-2-4-2s-1.3 2-4 2c-1.7 0-3-1-5-2"/><path d="M4 12V8a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v4"/><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/></svg>`,
			sofa: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 9V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v2"/><path d="M4 11v9a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-9"/><path d="M4 11h16"/><path d="M12 11v4"/></svg>`,
			'gamepad-2': `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="12" x="2" y="6" rx="2"/><path d="M6 12h4m-2-2v4"/><circle cx="17" cy="12" r="1.5"/><path d="M16.5 8.5v.01"/><path d="M10 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M6 10H4a2 2 0 0 1-2-2V4c0-1.1.9-2 2-2h3.18a2 2 0 0 1 1.96 1.68L10 6"/></svg>`,
			mountain: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m8 3 4 8 5-5 5 15H2L8 3z"/></svg>`,
			scan: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 7 5-5 5 5"/><path d="M8 2v10"/><path d="m21 17-5 5-5-5"/><path d="M16 22V12"/></svg>`,
		};
		return icons[name] || icons.utensils;
	}
</script>

<svelte:head>
	<title>Split Bill - Home</title>
</svelte:head>

<div class="w-full min-h-screen flex flex-col bg-surface-50 dark:bg-surface-900 text-text-primary dark:text-text-primary">
	<!-- Decorative background -->
	<div class="pointer-events-none absolute inset-0 overflow-hidden -z-10">
		<div class="absolute -top-24 -right-20 h-72 w-72 rounded-full bg-primary-500/15 dark:bg-primary-500/10 blur-2xl"></div>
		<div class="absolute top-28 -left-24 h-72 w-72 rounded-full bg-success/10 blur-2xl"></div>
		<div class="absolute bottom-40 -right-24 h-72 w-72 rounded-full bg-warning/10 blur-2xl"></div>
	</div>

	<!-- Header -->
	<header class="shrink-0 px-4 relative z-10" style="padding-top: max(env(safe-area-inset-top), 3.5rem);">
		<div class="max-w-lg mx-auto flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="h-11 w-11 rounded-2xl bg-primary-500 shadow-md flex items-center justify-center">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-inverted"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
				</div>
				<div class="leading-tight">
					<p class="text-label font-semibold text-text-primary">Split Bill</p>
					<p class="text-caption text-text-secondary">Make it fair in seconds</p>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<button type="button" class="h-11 w-11 rounded-2xl bg-surface-0 shadow-md border border-surface-200 flex items-center justify-center active:scale-[0.99] hover:bg-surface-50 focus-visible:ring-2 focus-visible:ring-primary-500 transition-colors" aria-label="Notifications">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
				</button>
				<button type="button" class="h-11 w-11 rounded-2xl bg-surface-0 shadow-md border border-surface-200 flex items-center justify-center active:scale-[0.99] hover:bg-surface-50 focus-visible:ring-2 focus-visible:ring-primary-500 transition-colors" aria-label="Profile">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
				</button>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="flex-1 overflow-y-auto px-4 pt-5 pb-[120px] relative z-0 no-scrollbar">
		<div class="max-w-lg mx-auto space-y-section">
		<!-- Hero Card Section -->
		<section class="rounded-3xl bg-surface-0 dark:bg-surface-800 shadow-card border border-surface-200 dark:border-surface-700 p-5 relative overflow-hidden animate-fade-in" aria-label="Quick stats and currency selection">
			<!-- Currency & Title -->
			<div class="flex items-start justify-between gap-4 mb-5">
				<div class="flex-1">
					<!-- Currency Pill -->
					<button onclick={() => showCurrencyConverter = true} class="mb-3 inline-flex items-center gap-1.5 rounded-full bg-surface-100 dark:bg-surface-700 pl-3 pr-2 py-1 text-caption font-bold text-text-secondary hover:bg-surface-200 dark:hover:bg-surface-600 active:scale-95 focus-visible:ring-2 focus-visible:ring-primary-500/50 transition-transform">
						<span class="w-4 h-4 rounded-full bg-surface-0 dark:bg-surface-600 flex items-center justify-center shadow-sm text-caption">Rp</span>
						IDR
						<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="m6 9 6 6 6-6"/></svg>
					</button>
					<h1 class="text-heading font-extrabold tracking-tight text-text-primary leading-tight">Split bills easily with friends</h1>
				</div>
				<div class="shrink-0">
					<div class="h-14 w-14 rounded-3xl bg-primary-50 dark:bg-primary-900/30 border border-primary-500/20 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-600 dark:text-primary-400"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
					</div>
				</div>
			</div>

			<!-- Action Buttons -->
			<div class="grid grid-cols-2 gap-3 mb-6">
				<a href="/split" class="h-12 min-h-[44px] rounded-2xl bg-primary-500 shadow-md flex items-center justify-center gap-2 text-text-inverted font-semibold active:scale-[0.99] focus-visible:ring-2 focus-visible:ring-primary-500/50 transition-transform hover:bg-primary-600 hover:shadow-lg animate-slide-in-right animate-delay-100">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-inverted"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
					<span class="text-label">New Split</span>
				</a>
				<a href="/receipt" class="h-12 min-h-[44px] rounded-2xl bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 shadow-md flex items-center justify-center gap-2 text-text-primary dark:text-text-inverted font-semibold active:scale-[0.99] focus-visible:ring-2 focus-visible:ring-primary-500 transition-transform">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-600 dark:text-primary-400"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
					<span class="text-label">Scan Receipt</span>
				</a>
			</div>

			<!-- Saved Templates -->
			<div class="mb-6">
				<div class="flex items-center justify-between mb-3">
					<h2 class="text-caption font-bold text-text-tertiary uppercase tracking-wider">Saved Templates</h2>
					<button class="text-primary-600 text-caption font-semibold active:opacity-70 focus-visible:ring-2 focus-visible:ring-primary-500/50">Edit</button>
				</div>
				<div class="flex gap-3 overflow-x-auto pb-2 -mx-5 px-5 no-scrollbar">
					{#each templates as template}
						<button class="shrink-0 flex flex-col items-center gap-2 w-[72px] group focus-visible:ring-2 focus-visible:ring-primary-500/50">
							<div class="{getColorClasses(template.color, 'bg')} border {getColorClasses(template.color, 'border')} {getColorClasses(template.color, 'text')} h-[52px] w-[52px] rounded-2xl flex items-center justify-center group-active:scale-95 transition-transform">
								{@html getIcon(template.icon)}
							</div>
							<span class="text-caption font-medium text-text-secondary text-center leading-tight">{template.name}{template.count > 0 ? ` (${template.count})` : ''}</span>
						</button>
					{/each}
					<button class="shrink-0 flex flex-col items-center gap-2 w-[72px] group focus-visible:ring-2 focus-visible:ring-primary-500/50">
						<div class="h-[52px] w-[52px] rounded-2xl bg-surface-50 dark:bg-surface-700 border border-surface-100 dark:border-surface-600 text-text-tertiary flex items-center justify-center group-active:scale-95 transition-transform">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
						</div>
						<span class="text-caption font-medium text-text-secondary text-center leading-tight">Add</span>
					</button>
				</div>
			</div>

			<!-- Quick Stats -->
			<div class="flex gap-2 overflow-x-auto pb-1 -mx-5 px-5 no-scrollbar">
				<div class="flex-1 min-w-[100px] shrink-0 rounded-2xl bg-primary-50 dark:bg-primary-900/30 border border-primary-500/15 px-3 py-2">
					<p class="text-caption text-text-secondary">This month</p>
					<p class="text-label font-bold text-text-primary">Rp 3.850k</p>
				</div>
				<div class="flex-1 min-w-[90px] shrink-0 rounded-2xl bg-success/10 dark:bg-success/20 border border-success/20 px-3 py-2">
					<p class="text-caption text-text-secondary">Settled</p>
					<p class="text-label font-bold text-text-primary">{settledCount} of {totalCount}</p>
				</div>
				<div class="flex-1 min-w-[90px] shrink-0 rounded-2xl bg-warning/10 dark:bg-warning/20 border border-warning/20 px-3 py-2">
					<p class="text-caption text-text-secondary">Pending</p>
					<p class="text-label font-bold text-text-primary">{pendingCount} splits</p>
				</div>
			</div>
		</section>

		<!-- Your Groups -->
		<section aria-label="Your groups">
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-section font-bold text-text-primary">Your Groups</h2>
				<a href="/groups/new" class="text-label font-semibold text-primary-600">+ Create Group</a>
			</div>
			<div class="flex gap-3 overflow-x-auto pb-4 -mx-4 px-4 no-scrollbar">
				{#each groups as group}
					<a href="/groups/{group.id}" class="shrink-0 w-36 sm:w-40 p-4 rounded-3xl bg-surface-0 dark:bg-surface-800 shadow-card border border-surface-200 dark:border-surface-700 active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-primary-500/50 transition-transform block">
						<div class="flex items-center gap-3 mb-3">
							<div class="{getColorClasses(group.color, 'bg')} {getColorClasses(group.color, 'text')} h-10 w-10 rounded-xl flex items-center justify-center">
								{@html getIcon(group.icon)}
							</div>
							<div>
								<p class="text-label font-bold text-text-primary truncate">{group.name}</p>
								<p class="text-caption text-text-tertiary">{group.members} members</p>
							</div>
						</div>
						<p class="text-caption text-text-tertiary font-medium">Last split {group.lastActivity}</p>
					</a>
				{/each}
			</div>
		</section>

		<!-- Activity Feed -->
		<section aria-label="Recent activity">
			<h2 class="px-1 mb-3 text-label font-bold text-text-primary">Activity</h2>
			<div class="space-y-2">
				{#each activities as activity}
					<div class="flex items-center gap-3 p-3 rounded-2xl bg-surface-0 dark:bg-surface-800 border border-surface-100 dark:border-surface-700">
						<div class="h-8 w-8 rounded-full {activity.personColor === 'sky' ? 'bg-info/10' : activity.personColor === 'emerald' ? 'bg-success/10' : 'bg-surface-200'} border border-surface-0 dark:border-surface-700 flex items-center justify-center shrink-0">
							<span class="text-caption font-bold text-text-primary dark:text-text-primary">{activity.person[0]}</span>
						</div>
						<p class="text-caption text-text-primary leading-snug flex-1"><span class="font-bold text-text-primary">{activity.person}</span> {activity.action} <span class="font-semibold">{activity.target}</span>.</p>
						<span class="text-caption text-text-tertiary">{activity.time}</span>
					</div>
				{/each}
			</div>
		</section>

		<!-- Spending Insights -->
		<section aria-label="Spending insights">
			<div class="rounded-3xl bg-text-primary text-text-inverted p-5 shadow-lg relative overflow-hidden">
				<div class="relative z-10 flex items-start justify-between">
					<div>
						<p class="text-caption font-medium text-text-tertiary mb-1">Total Spent (Feb)</p>
						<h2 class="text-heading font-bold">Rp 3.850k</h2>
					</div>
					<a href="#insights" class="px-3 py-1.5 rounded-xl bg-surface-800 text-caption font-medium text-text-secondary hover:bg-surface-700 transition-colors inline-block">
						Insights
					</a>
				</div>

				<!-- Simple Bar Chart -->
				<div class="mt-6 flex items-end justify-between gap-2 h-24 px-1">
					<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
						<div class="w-full bg-surface-800 rounded-t-lg h-[40%] group-hover:bg-primary-500 transition-colors"></div>
						<span class="text-caption text-text-tertiary text-center">Dec</span>
					</div>
					<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
						<div class="w-full bg-surface-800 rounded-t-lg h-[65%] group-hover:bg-primary-500 transition-colors"></div>
						<span class="text-caption text-text-tertiary text-center">Jan</span>
					</div>
					<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
						<div class="w-full bg-primary-500 rounded-t-lg h-[85%] relative shadow-[0_0_15px_rgba(14,165,233,0.5)]"></div>
						<span class="text-caption text-text-inverted font-bold text-center">Feb</span>
					</div>
					<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
						<div class="w-full bg-surface-800/50 border border-surface-700 border-dashed rounded-t-lg h-[60%]" style="background-image: repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(255,255,255,0.05) 5px, rgba(255,255,255,0.05) 10px);"></div>
						<span class="text-caption text-text-tertiary text-center">Mar</span>
					</div>
				</div>
			</div>
		</section>

		<!-- Recent Splits -->
		<section class="space-y-3">
			<div class="flex items-center justify-between px-1">
				<p class="text-section font-bold text-text-primary">Recent Splits</p>
				<a href="/history" class="text-label font-semibold text-primary-600 active:scale-[0.99] focus-visible:ring-2 focus-visible:ring-primary-500/50">View all</a>
			</div>

			{#each recentSplits as split, index}
				{@const statusColors = getStatusClasses(split.status)}
				<article class="rounded-3xl bg-surface-0 dark:bg-surface-800 shadow-card border border-surface-200 dark:border-surface-700 p-4 hover:shadow-elevated transition-all duration-200 group animate-slide-in" style="animation-delay: {Math.min(index * 100 + 400, 700)}ms;">
					<div class="flex items-start gap-3">
						<div class="{getColorClasses(split.color, 'bg')} border {getColorClasses(split.color, 'border')} {getColorClasses(split.color, 'text')} h-12 w-12 rounded-2xl flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform duration-200">
							{@html getIcon(split.icon)}
						</div>
						<div class="min-w-0 flex-1">
							<div class="flex items-start justify-between gap-2 sm:gap-3">
								<div class="min-w-0 flex-1">
									<p class="text-label font-semibold text-text-primary truncate">{split.title}</p>
									<p class="mt-0.5 text-caption text-text-secondary">{split.date} • {split.people} people</p>
								</div>
								<div class="shrink-0 flex flex-col sm:items-end items-start gap-1">
									<p class="text-label font-extrabold text-text-primary">{split.amount}</p>
									<span class="{statusColors.bg} {statusColors.text} inline-flex items-center rounded-full px-2 py-1 text-caption font-bold uppercase tracking-wide whitespace-nowrap">
										{split.status}
									</span>
								</div>
							</div>
						</div>
					</div>
					<div class="mt-3 flex items-center justify-between gap-3 pl-[60px]">
						<div class="flex -space-x-2">
							<div class="h-7 w-7 rounded-full bg-surface-200 dark:bg-surface-700 border-2 border-surface-0 dark:border-surface-800 flex items-center justify-center text-caption font-bold text-text-secondary dark:text-text-tertiary">A</div>
							<div class="h-7 w-7 rounded-full bg-info/10 border-2 border-surface-0 dark:border-surface-800 flex items-center justify-center text-caption font-bold text-text-secondary dark:text-text-tertiary">M</div>
							<div class="h-7 w-7 rounded-full bg-success/10 border-2 border-surface-0 dark:border-surface-800 flex items-center justify-center text-caption font-bold text-text-secondary dark:text-text-tertiary">J</div>
						</div>
						<a href="/split/{split.id}" class="px-4 py-2 rounded-xl bg-surface-100 dark:bg-surface-700 text-text-primary dark:text-text-inverted text-caption font-bold shadow-sm active:scale-95 transition-transform">
							Details
						</a>
					</div>
				</article>
			{/each}
		</section>

		<!-- Friendly helper card -->
		<section class="rounded-3xl bg-primary-600 dark:bg-primary-900 shadow-card p-4 text-text-inverted relative overflow-hidden">
			<div class="absolute right-0 top-0 h-32 w-32 bg-surface-0/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
			<div class="relative z-10 flex items-start gap-3">
				<div class="h-10 w-10 rounded-xl bg-surface-0/20 flex items-center justify-center shadow-sm">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
				</div>
				<div class="min-w-0">
					<p class="text-label font-bold">Scanning Tips</p>
					<p class="mt-1 text-caption text-primary-100">Ensure good lighting for best results. We'll handle the math!</p>
				</div>
			</div>
		</section>
		</div>
	</main>
</div>

{#if showCurrencyConverter}
	<CurrencyConverter onClose={() => showCurrencyConverter = false} />
{/if}
