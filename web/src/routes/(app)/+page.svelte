<script lang="ts">
	import { onMount } from 'svelte';
	import { currencyStore, analyticsStore } from '$lib/stores';
	import { goto } from '$app/navigation';

	let monthlySpending = $state(3850000);
	let settledCount = $state(5);
	let totalCount = $state(7);
	let pendingCount = $state(2);

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

<div class="w-full h-screen flex flex-col bg-primary-50 text-slate-900 overflow-hidden">
	<!-- Decorative background -->
	<div class="pointer-events-none absolute inset-0 overflow-hidden">
		<div class="absolute -top-24 -right-20 h-72 w-72 rounded-full bg-primary-500/15 blur-2xl decorative-blur"></div>
		<div class="absolute top-28 -left-24 h-72 w-72 rounded-full bg-emerald-400/10 blur-2xl decorative-blur"></div>
		<div class="absolute bottom-40 -right-24 h-72 w-72 rounded-full bg-amber-400/10 blur-2xl decorative-blur"></div>
	</div>

	<!-- Header -->
	<header class="shrink-0 pt-14 px-4 relative z-10">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="h-11 w-11 rounded-2xl bg-primary-500 shadow-md flex items-center justify-center">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
				</div>
				<div class="leading-tight">
					<p class="text-sm font-semibold text-slate-900">Split Bill</p>
					<p class="text-xs text-slate-600">Make it fair in seconds</p>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<button type="button" class="h-11 w-11 rounded-2xl bg-white shadow-md border border-slate-200 flex items-center justify-center active:scale-[0.99]">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
				</button>
				<button type="button" class="h-11 w-11 rounded-2xl bg-white shadow-md border border-slate-200 flex items-center justify-center active:scale-[0.99]">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
				</button>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="flex-1 overflow-y-auto px-4 pt-5 pb-[120px] relative z-0 no-scrollbar">

		<!-- Hero Card Section -->
		<section class="rounded-3xl bg-white shadow-md border border-slate-200 p-5 relative overflow-hidden" style="max-width: calc(100vw - 2rem);">
			<!-- Currency & Title -->
			<div class="flex items-start justify-between gap-4 mb-5">
				<div>
					<!-- Currency Pill -->
					<button class="mb-3 inline-flex items-center gap-1.5 rounded-full bg-slate-100 pl-3 pr-2 py-1 text-xs font-bold text-slate-700 hover:bg-slate-200 active:scale-95 transition-transform">
						<span class="w-4 h-4 rounded-full bg-white flex items-center justify-center shadow-sm text-xs">Rp</span>
						IDR
						<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m6 9 6 6 6-6"/></svg>
					</button>
					<h1 class="text-2xl font-extrabold tracking-tight text-slate-900 leading-tight">Split bills easily<br>with friends</h1>
				</div>
				<div class="shrink-0">
					<div class="h-14 w-14 rounded-3xl bg-primary-50 border border-primary-500/20 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-600"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
					</div>
				</div>
			</div>

			<!-- Action Buttons -->
			<div class="grid grid-cols-2 gap-3 mb-6">
				<a href="/split" class="h-12 min-h-[44px] rounded-2xl bg-primary-500 shadow-md flex items-center justify-center gap-2 text-white font-semibold active:scale-[0.99] transition-transform hover:bg-primary-600">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
					<span class="text-sm">Create New Bill</span>
				</a>
				<a href="/receipt" class="h-12 min-h-[44px] rounded-2xl bg-white border border-slate-200 shadow-md flex items-center justify-center gap-2 text-slate-900 font-semibold active:scale-[0.99] transition-transform hover:bg-slate-50">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-600"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
					<span class="text-sm">Scan Receipt</span>
				</a>
			</div>

			<!-- Saved Templates -->
			<div class="mb-6">
				<div class="flex items-center justify-between mb-3">
					<h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Saved Templates</h3>
					<button class="text-primary-600 text-xs font-semibold active:opacity-70">Edit</button>
				</div>
				<div class="flex gap-3 overflow-x-auto pb-2 -mx-5 px-5 no-scrollbar" style="max-width: calc(100vw - 2rem);">
					{#each templates as template}
						<button class="shrink-0 flex flex-col items-center gap-2 w-[72px] group">
							<div class="h-[52px] w-[52px] rounded-2xl bg-{template.color}-50 border border-{template.color}-100 text-{template.color}-500 flex items-center justify-center group-active:scale-95 transition-transform">
								{@html getIcon(template.icon)}
							</div>
							<span class="text-xs font-medium text-slate-600 text-center leading-tight">{template.name}{template.count > 0 ? ` (${template.count})` : ''}</span>
						</button>
					{/each}
					<button class="shrink-0 flex flex-col items-center gap-2 w-[72px] group">
						<div class="h-[52px] w-[52px] rounded-2xl bg-slate-50 border border-slate-100 text-slate-400 flex items-center justify-center group-active:scale-95 transition-transform">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
						</div>
						<span class="text-xs font-medium text-slate-600 text-center leading-tight">Add</span>
					</button>
				</div>
			</div>

			<!-- Quick Stats -->
			<div class="flex gap-2 overflow-x-auto pb-1 -mx-5 px-5 no-scrollbar" style="max-width: calc(100vw - 2rem);">
				<div class="shrink-0 rounded-2xl bg-primary-50 border border-primary-500/15 px-3 py-2 min-w-[120px]">
					<p class="text-xs text-slate-600">This month</p>
					<p class="text-sm font-bold text-slate-900">Rp 3.850k</p>
				</div>
				<div class="shrink-0 rounded-2xl bg-emerald-50 border border-emerald-500/15 px-3 py-2 min-w-[100px]">
					<p class="text-xs text-slate-600">Settled</p>
					<p class="text-sm font-bold text-slate-900">{settledCount} of {totalCount}</p>
				</div>
				<div class="shrink-0 rounded-2xl bg-amber-50 border border-amber-500/15 px-3 py-2 min-w-[100px]">
					<p class="text-xs text-slate-600">Pending</p>
					<p class="text-sm font-bold text-slate-900">{pendingCount} splits</p>
				</div>
			</div>
		</section>

		<!-- Your Groups -->
		<section class="mt-6">
			<div class="flex items-center justify-between px-1 mb-3">
				<h3 class="text-lg font-bold text-slate-900">Your Groups</h3>
				<a href="#groups" class="text-sm font-semibold text-primary-600">See all</a>
			</div>
			<div class="flex gap-3 overflow-x-auto pb-4 -mx-4 px-4 no-scrollbar" style="max-width: calc(100vw - 2rem);">
				{#each groups as group}
					<a href="#group-{group.id}" class="shrink-0 w-40 p-4 rounded-3xl bg-white shadow-sm border border-slate-200 active:scale-[0.98] transition-transform block">
						<div class="flex items-center gap-3 mb-3">
							<div class="h-10 w-10 rounded-xl bg-{group.color}-100 text-{group.color}-600 flex items-center justify-center">
								{@html getIcon(group.icon)}
							</div>
							<div>
								<p class="text-sm font-bold text-slate-900">{group.name}</p>
								<p class="text-xs text-slate-500">{group.members} members</p>
							</div>
						</div>
						<p class="text-xs text-slate-400 font-medium">Last split {group.lastActivity}</p>
					</a>
				{/each}
			</div>
		</section>

		<!-- Activity Feed -->
		<section class="mt-2 mb-6">
			<h3 class="px-1 mb-3 text-sm font-bold text-slate-900">Activity</h3>
			<div class="space-y-2">
				{#each activities as activity}
					<div class="flex items-center gap-3 p-3 rounded-2xl bg-white/60 border border-white/50 backdrop-blur-sm">
						<div class="h-8 w-8 rounded-full bg-{activity.personColor}-200 border border-white flex items-center justify-center shrink-0">
							<span class="text-xs font-bold text-{activity.personColor}-800">{activity.person[0]}</span>
						</div>
						<p class="text-xs text-slate-700 leading-snug flex-1"><span class="font-bold text-slate-900">{activity.person}</span> {activity.action} <span class="font-semibold">{activity.target}</span>.</p>
						<span class="text-xs text-slate-400">{activity.time}</span>
					</div>
				{/each}
			</div>
		</section>

		<!-- Spending Insights -->
		<section class="mt-4 mb-8">
			<div class="rounded-3xl bg-slate-900 text-white p-5 shadow-lg relative overflow-hidden">
				<div class="relative z-10 flex items-start justify-between">
					<div>
						<p class="text-xs font-medium text-slate-400 mb-1">Total Spent (Feb)</p>
						<h2 class="text-2xl font-bold">Rp 3.850k</h2>
					</div>
					<a href="#insights" class="px-3 py-1.5 rounded-xl bg-slate-800 text-xs font-medium text-slate-300 hover:bg-slate-700 transition-colors inline-block">
						Insights
					</a>
				</div>

				<!-- Simple Bar Chart -->
				<div class="mt-6 flex items-end justify-between gap-2 h-24 px-1">
					<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
						<div class="w-full bg-slate-800 rounded-t-lg h-[40%] group-hover:bg-primary-500 transition-colors"></div>
						<span class="text-xs text-slate-500 text-center">Dec</span>
					</div>
					<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
						<div class="w-full bg-slate-800 rounded-t-lg h-[65%] group-hover:bg-primary-500 transition-colors"></div>
						<span class="text-xs text-slate-500 text-center">Jan</span>
					</div>
					<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
						<div class="w-full bg-primary-500 rounded-t-lg h-[85%] relative shadow-[0_0_15px_rgba(14,165,233,0.5)]"></div>
						<span class="text-xs text-white font-bold text-center">Feb</span>
					</div>
					<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
						<div class="w-full bg-slate-800/50 border border-slate-700 border-dashed rounded-t-lg h-[60%]" style="background-image: repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(255,255,255,0.05) 5px, rgba(255,255,255,0.05) 10px);"></div>
						<span class="text-xs text-slate-500 text-center">Mar</span>
					</div>
				</div>
			</div>
		</section>

		<!-- Recent Splits -->
		<section class="space-y-3">
			<div class="flex items-center justify-between px-1">
				<p class="text-lg font-bold text-slate-900">Recent Splits</p>
				<a href="/history" class="text-sm font-semibold text-primary-600 active:scale-[0.99]">View all</a>
			</div>

			{#each recentSplits as split}
				<article class="rounded-3xl bg-white shadow-md border border-slate-200 p-4">
					<div class="flex items-start gap-3">
						<div class="h-12 w-12 rounded-2xl bg-{split.color}-50 border border-{split.color}-500/15 flex items-center justify-center">
							{@html getIcon(split.icon)}
						</div>
						<div class="min-w-0 flex-1">
							<div class="flex items-start justify-between gap-3">
								<div class="min-w-0">
									<p class="text-sm font-semibold text-slate-900 truncate">{split.title}</p>
									<p class="mt-0.5 text-xs text-slate-600">{split.date} • {split.people} people</p>
								</div>
								<div class="text-right">
									<p class="text-sm font-extrabold text-slate-900">{split.amount}</p>
									<span class="mt-1 inline-flex items-center rounded-full bg-{split.status === 'Paid' ? 'emerald' : 'amber'}-100 text-{split.status === 'Paid' ? 'emerald' : 'amber'}-800 px-2 py-1 text-xs font-bold uppercase tracking-wide">
										{split.status}
									</span>
								</div>
							</div>
						</div>
					</div>
					<div class="mt-3 flex items-center justify-between gap-3 pl-[60px]">
						<div class="flex -space-x-2">
							<div class="h-7 w-7 rounded-full bg-slate-200 border-2 border-white flex items-center justify-center text-xs font-bold text-slate-600">A</div>
							<div class="h-7 w-7 rounded-full bg-sky-200 border-2 border-white flex items-center justify-center text-xs font-bold text-slate-600">M</div>
							<div class="h-7 w-7 rounded-full bg-emerald-200 border-2 border-white flex items-center justify-center text-xs font-bold text-slate-600">J</div>
						</div>
						<a href="/split/{split.id}" class="px-4 py-2 rounded-xl bg-slate-100 text-slate-900 text-xs font-bold shadow-sm active:scale-95 transition-transform">
							Details
						</a>
					</div>
				</article>
			{/each}
		</section>

		<!-- Friendly helper card -->
		<section class="mt-6 rounded-3xl bg-indigo-600 shadow-md p-4 text-white relative overflow-hidden" style="max-width: calc(100vw - 2rem);">
			<div class="absolute right-0 top-0 h-32 w-32 bg-white/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
			<div class="relative z-10 flex items-start gap-3">
				<div class="h-10 w-10 rounded-xl bg-white/20 flex items-center justify-center shadow-sm backdrop-blur-sm">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
				</div>
				<div class="min-w-0">
					<p class="text-sm font-bold">Scanning Tips</p>
					<p class="mt-1 text-xs text-indigo-100">Ensure good lighting for best results. We'll handle the math!</p>
				</div>
			</div>
		</section>
	</main>
</div>
