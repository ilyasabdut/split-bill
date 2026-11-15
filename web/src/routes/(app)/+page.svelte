<script lang="ts">
	import { get } from 'svelte/store';
	import { currencyStore, analyticsStore } from '$lib/stores';
	import { groupsStore } from '$lib/stores/groups';
	import { templatesStore } from '$lib/stores/templates';
	import { goto } from '$app/navigation';
	import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';
	import CurrencyConverter from '$lib/components/ui/CurrencyConverter.svelte';
	import { onMount } from 'svelte';

	let monthlySpending = $state(0);
	let settledCount = $state(0);
	let totalCount = $state(0);
	let pendingCount = $state(0);
	let showCurrencyConverter = $state(false);
	let monthlyChart = $state<{ label: string; amount: number; isCurrent: boolean }[]>([]);

	let groups = $state<{ id: string; name: string; icon: string; color: string; members: number; lastActivity: string }[]>([]);

	const activities = $state<{ person: string; personColor: string; action: string; target: string; type: string; time: string }[]>([]);

	let recentSplits = $state<{ id: string; title: string; date: string; people: number; amount: string; status: string; icon: string; color: string; initials: string[] }[]>([]);

	let templates = $state<{ id: string; name: string; count: number; icon: string; color: string }[]>([]);

	function formatRelativeTime(timestamp: number): string {
		const diff = Date.now() - timestamp;
		const minutes = Math.floor(diff / 60000);
		const hours = Math.floor(diff / 3600000);
		const days = Math.floor(diff / 86400000);
		if (minutes < 1) return 'now';
		if (minutes < 60) return `${minutes}m`;
		if (hours < 24) return `${hours}h`;
		if (days < 7) return `${days}d`;
		return `${Math.floor(days / 7)}w`;
	}

	onMount(() => {
		loadDashboard();
	});

	const groupColors = ['violet', 'pink', 'emerald', 'sky', 'orange'];
	const templateIcons: Record<string, string> = { lunch: 'utensils', rent: 'home', trip: 'plane', dinner: 'utensils', groceries: 'car' };
	const templateColors: Record<string, string> = { lunch: 'orange', rent: 'emerald', trip: 'sky', dinner: 'orange', groceries: 'pink' };

	async function loadDashboard() {
		currencyStore.init();
		analyticsStore.loadAnalytics().catch(() => {});

		Promise.all([
			groupsStore.loadGroups(),
			templatesStore.loadTemplates()
		]).then(() => {
			const g = get(groupsStore.groups);
			groups = g.map((group, i) => ({
				id: String(group.id),
				name: group.name,
				icon: 'sofa',
				color: groupColors[i % groupColors.length],
				members: group.members?.length || 0,
				lastActivity: group.created_at ? formatRelativeTime(new Date(group.created_at).getTime()) : ''
			}));

			const t = get(templatesStore.templates);
			templates = t.map((tmpl) => ({
				id: String(tmpl.id),
				name: tmpl.name,
				count: 0,
				icon: templateIcons[tmpl.name.toLowerCase()] || 'utensils',
				color: templateColors[tmpl.name.toLowerCase()] || 'orange'
			}));
		}).catch(() => {});

		try {
			const indexedDB = await getIndexedDB();
			const items = await indexedDB.getAll<any>(STORES.SPLITS);

			const sorted = items
				.filter((item: any) => item.createdAt)
				.sort((a: any, b: any) => b.createdAt - a.createdAt);

			totalCount = sorted.length;
			settledCount = sorted.filter((item: any) => item.status === 'completed').length;
			pendingCount = sorted.filter((item: any) => item.status !== 'completed').length;

			const now = new Date();
			const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).getTime();
			monthlySpending = sorted
				.filter((item: any) => item.createdAt >= monthStart)
				.reduce((sum: number, item: any) => sum + (item.total || 0), 0);

			// Build last 4 months chart
			const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
			monthlyChart = [];
			for (let i = 3; i >= 0; i--) {
				const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
				const mStart = d.getTime();
				const mEnd = new Date(d.getFullYear(), d.getMonth() + 1, 1).getTime();
				const amount = sorted
					.filter((item: any) => item.createdAt >= mStart && item.createdAt < mEnd)
					.reduce((sum: number, item: any) => sum + (item.total || 0), 0);
				monthlyChart.push({ label: monthNames[d.getMonth()], amount, isCurrent: i === 0 });
			}

			recentSplits = sorted.slice(0, 3).map((item: any) => {
				const names = item.people || Object.keys(item.results || {});
				const people = names.length;
				const total = item.total || 0;
				const date = new Date(item.createdAt);
				const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
				return {
					id: String(item.id),
					title: names.join(', ') || 'Split',
					date: `${months[date.getMonth()]} ${date.getDate()}`,
					people,
					amount: total >= 1000000 ? `Rp ${(total / 1000000).toFixed(1)}M` : `Rp ${(total / 1000).toFixed(0)}k`,
					status: item.status === 'completed' ? 'Paid' : 'Unpaid',
					icon: 'utensils',
					color: item.status === 'completed' ? 'emerald' : 'primary',
					initials: names.slice(0, 3).map((n: string) => n.charAt(0).toUpperCase())
				};
			});

			// Populate activity feed from recent splits
			const colors = ['sky', 'emerald', 'amber'];
			activities.length = 0;
			sorted.slice(0, 5).forEach((item: any, i: number) => {
				const names = item.people || Object.keys(item.results || {});
				const person = names[0] || 'Someone';
				activities.push({
					person,
					personColor: colors[i % colors.length],
					action: 'created a split with',
					target: names.slice(1).join(', ') || 'others',
					type: 'split',
					time: formatRelativeTime(item.createdAt)
				});
			});
		} catch (err) {
			console.error('Failed to load dashboard data:', err);
		}
	}

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
				<button type="button" onclick={() => goto('/send-reminder')} class="h-11 w-11 rounded-2xl bg-surface-0 shadow-md border border-surface-200 flex items-center justify-center active:scale-[0.99] hover:bg-surface-50 focus-visible:ring-2 focus-visible:ring-primary-500 transition-colors" aria-label="Notifications">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
				</button>
				<button type="button" onclick={() => goto('/settings')} class="h-11 w-11 rounded-2xl bg-surface-0 shadow-md border border-surface-200 flex items-center justify-center active:scale-[0.99] hover:bg-surface-50 focus-visible:ring-2 focus-visible:ring-primary-500 transition-colors" aria-label="Profile and Settings">
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
			<div class="flex items-start justify-between gap-4 mb-5">
				<div class="flex-1">
					<button onclick={() => showCurrencyConverter = true} class="mb-3 inline-flex items-center gap-1.5 rounded-full bg-surface-100 dark:bg-surface-700 pl-3 pr-2 py-1 text-caption font-bold text-text-secondary hover:bg-surface-200 dark:hover:bg-surface-600 active:scale-95 focus-visible:ring-2 focus-visible:ring-primary-500/50 transition-transform">
						<span class="w-5 h-5 rounded-full flex items-center justify-center shadow-sm text-caption">🇮🇩</span>
						IDR
						<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="m6 9 6 6 6-6"/></svg>
					</button>
					<h1 class="text-heading font-extrabold tracking-tight text-text-primary leading-tight">Split bills easily with friends</h1>
				</div>
				<div class="shrink-0">
					<div class="h-14 w-14 rounded-xl bg-primary-50 dark:bg-primary-900/30 border border-primary-500/20 flex items-center justify-center">
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
					<a href="/split" class="text-primary-600 text-caption font-semibold active:opacity-70 focus-visible:ring-2 focus-visible:ring-primary-500/50">Edit</a>
				</div>
				<div class="flex gap-3 overflow-x-auto pb-2 -mx-5 px-5 no-scrollbar">
					{#each templates as template}
						<button onclick={() => goto('/split')} class="shrink-0 flex flex-col items-center gap-2 w-[72px] group focus-visible:ring-2 focus-visible:ring-primary-500/50">
							<div class="{getColorClasses(template.color, 'bg')} border {getColorClasses(template.color, 'border')} {getColorClasses(template.color, 'text')} h-[52px] w-[52px] rounded-2xl flex items-center justify-center group-active:scale-95 transition-transform">
								{@html getIcon(template.icon)}
							</div>
							<span class="text-caption font-medium text-text-secondary text-center leading-tight">{template.name}{template.count > 0 ? ` (${template.count})` : ''}</span>
						</button>
					{/each}
					<button onclick={() => goto('/split')} class="shrink-0 flex flex-col items-center gap-2 w-[72px] group focus-visible:ring-2 focus-visible:ring-primary-500/50">
						<div class="h-[52px] w-[52px] rounded-2xl bg-surface-50 dark:bg-surface-700 border border-surface-100 dark:border-surface-600 text-text-tertiary flex items-center justify-center group-active:scale-95 transition-transform">
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
						</div>
						<span class="text-caption font-medium text-text-secondary text-center leading-tight">Add</span>
					</button>
				</div>
			</div>

			<div class="flex gap-2 overflow-x-auto pb-1 -mx-5 px-5 no-scrollbar">
				<div class="flex-1 min-w-[100px] shrink-0 rounded-2xl bg-primary-600 dark:bg-primary-700 border border-primary-500 px-3 py-2 shadow-card">
					<p class="text-caption text-primary-100">This month</p>
					<p class="text-label font-bold text-text-inverted">{monthlySpending >= 1000000 ? `Rp ${(monthlySpending / 1000000).toFixed(1)}M` : monthlySpending >= 1000 ? `Rp ${(monthlySpending / 1000).toFixed(0)}k` : `Rp ${monthlySpending}`}</p>
				</div>
				<div class="flex-1 min-w-[90px] shrink-0 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-700 px-3 py-2">
					<p class="text-caption text-text-secondary">Settled</p>
					<p class="text-label font-bold text-emerald-700 dark:text-emerald-400">{settledCount} of {totalCount}</p>
				</div>
				<div class="flex-1 min-w-[90px] shrink-0 rounded-2xl bg-amber-100 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-700 px-3 py-2">
					<p class="text-caption text-text-secondary">Pending</p>
					<p class="text-label font-bold text-amber-700 dark:text-amber-400">{pendingCount} splits</p>
				</div>
			</div>
		</section>

		<!-- Spending Insights -->
		<section aria-label="Spending insights">
			<div class="rounded-3xl bg-primary-600 dark:bg-primary-900 text-text-inverted p-6 shadow-xl relative overflow-hidden">
				<!-- Decorative circles -->
				<div class="absolute top-0 right-0 w-32 h-32 bg-surface-0/10 rounded-full -mr-10 -mt-10 blur-2xl"></div>
				<div class="absolute bottom-0 left-0 w-24 h-24 bg-surface-0/5 rounded-full -ml-8 -mb-8 blur-xl"></div>

				<div class="relative z-10">
					<div class="flex items-start justify-between">
						<p class="text-primary-100 text-label font-medium">Total spending this month</p>
						<a href="/history" class="bg-surface-0/20 px-2.5 py-1 rounded-lg text-caption font-semibold text-text-inverted flex items-center gap-1 hover:bg-surface-0/30 transition-colors">
							<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
							{totalCount} splits
						</a>
					</div>
					<h2 class="text-heading font-bold tracking-tight mt-2 tabular-nums">{monthlySpending > 0 ? `Rp ${monthlySpending.toLocaleString('id-ID')}` : 'Rp 0'}</h2>
					<p class="text-caption text-primary-200 mt-1 opacity-80">This month's total</p>
				</div>

				<!-- Simple Bar Chart -->
				<div class="relative z-10 mt-6 flex items-end justify-between gap-2 h-20 px-1">
					{#each monthlyChart as month}
						{@const maxAmount = Math.max(...monthlyChart.map(m => m.amount), 1)}
						{@const height = month.amount > 0 ? Math.max(10, (month.amount / maxAmount) * 100) : 5}
						<div class="w-full flex flex-col justify-end gap-1 group cursor-pointer">
							<div class="w-full rounded-t-lg transition-colors {month.isCurrent ? 'bg-surface-0 shadow-[0_0_15px_rgba(255,255,255,0.3)]' : 'bg-surface-0/20 group-hover:bg-surface-0/40'}" style="height: {height}%"></div>
							<span class="text-caption text-center {month.isCurrent ? 'text-text-inverted font-bold' : 'text-primary-200'}">{month.label}</span>
						</div>
					{/each}
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
		<section aria-label="Recent activity" aria-live="polite">
			<h2 class="px-1 mb-3 text-label font-bold text-text-primary">Activity</h2>
			<div class="space-y-2">
				{#each activities as activity}
					<div class="flex items-center gap-3 p-3 rounded-3xl bg-surface-0 dark:bg-surface-800 border border-surface-100 dark:border-surface-700">
						<div class="h-8 w-8 rounded-full {activity.personColor === 'sky' ? 'bg-info/20' : activity.personColor === 'emerald' ? 'bg-success/20' : 'bg-surface-200'} border border-surface-0 dark:border-surface-700 flex items-center justify-center shrink-0">
							<span class="text-caption font-bold {activity.personColor === 'sky' ? 'text-info' : activity.personColor === 'emerald' ? 'text-success' : 'text-text-primary'}">{activity.person[0]}</span>
						</div>
						<p class="text-caption text-text-primary leading-snug flex-1"><span class="font-bold text-text-primary">{activity.person}</span> {activity.action} <span class="font-semibold">{activity.target}</span>.</p>
						<span class="text-caption text-text-tertiary">{activity.time}</span>
					</div>
				{/each}
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
							{#each split.initials as initial}
								<div class="h-7 w-7 rounded-full bg-surface-200 dark:bg-surface-700 border-2 border-surface-0 dark:border-surface-800 flex items-center justify-center text-caption font-bold text-text-secondary dark:text-text-tertiary">{initial}</div>
							{/each}
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
