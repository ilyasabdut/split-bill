<script lang="ts">
	import { page } from '$app/stores';

	const groupId = $derived($page.params.id);

	const group = {
		id: groupId,
		name: 'Roomies',
		description: 'Monthly bills and shared expenses',
		createdAt: Date.now() - 86400000 * 30,
		members: [
			{ id: '1', name: 'You', email: 'you@email.com', color: 'indigo', balance: 125000, role: 'admin' },
			{ id: '2', name: 'Sarah', email: 'sarah@email.com', color: 'emerald', balance: -85000, role: 'member' },
			{ id: '3', name: 'Mike', email: 'mike@email.com', color: 'rose', balance: -40000, role: 'member' },
			{ id: '4', name: 'Alex', email: 'alex@email.com', color: 'amber', balance: 0, role: 'member' },
		],
		receipts: [
			{ id: '1', title: 'Grocery Run', date: 'Feb 18', amount: 450000, status: 'settled', paidBy: 'You', splitBetween: 4 },
			{ id: '2', title: 'Electricity Bill', date: 'Feb 15', amount: 320000, status: 'pending', paidBy: 'Sarah', splitBetween: 4 },
			{ id: '3', title: 'Internet', date: 'Feb 10', amount: 150000, status: 'settled', paidBy: 'Mike', splitBetween: 4 },
			{ id: '4', title: 'Water Bill', date: 'Feb 5', amount: 85000, status: 'settled', paidBy: 'You', splitBetween: 4 },
		],
		totalSpent: 1005000,
		thisMonth: 450000,
	};

	const totalOwed = group.members.filter(m => m.balance < 0).reduce((sum, m) => sum + Math.abs(m.balance), 0);
	const totalOwing = group.members.filter(m => m.balance > 0).reduce((sum, m) => sum + m.balance, 0);

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}

	function getInitials(name: string): string {
		return name.charAt(0).toUpperCase();
	}
</script>

<svelte:head>
	<title>{group.name} - Split Bill</title>
	<meta name="color-scheme" content="light" />
</svelte:head>

<div class="w-full min-h-dvh flex flex-col bg-surface-50 text-text-primary font-sans">
	<!-- Decorative background -->
	<div class="pointer-events-none absolute inset-0 overflow-hidden -z-10">
		<div class="absolute -top-24 -right-20 h-72 w-72 rounded-full bg-indigo-500/15 blur-2xl"></div>
		<div class="absolute top-28 -left-24 h-72 w-72 rounded-full bg-rose-400/10 blur-2xl"></div>
	</div>

	<!-- Header -->
	<header class="shrink-0 px-4" style="padding-top: max(env(safe-area-inset-top), 3rem);">
		<div class="flex items-center justify-between max-w-lg mx-auto">
			<a href="/" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-2xl bg-surface-0 shadow-md border border-surface-200 active:scale-95 transition-transform hover:bg-surface-50" aria-label="Go back home">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="m15 18-6-6 6-6"/><path d="M18 6 6 18"/></svg>
			</a>
			<div class="text-center">
				<div class="text-xs font-bold text-text-secondary uppercase tracking-wider">Group</div>
				<h1 class="text-lg font-black tracking-tight text-text-primary">{group.name}</h1>
			</div>
			<button type="button" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-2xl bg-surface-0 shadow-md border border-surface-200 active:scale-95 transition-transform hover:bg-surface-50" aria-label="More options">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
			</button>
		</div>
	</header>

	<!-- Main Content -->
	<main class="flex-1 overflow-y-auto px-4 py-4 space-y-5 max-w-lg mx-auto w-full" style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 2rem);">

		<!-- Summary Card -->
		<section class="rounded-3xl bg-indigo-600 shadow-xl p-5 text-white relative overflow-hidden">
			<div class="absolute right-0 top-0 h-40 w-40 bg-surface-0/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>

			<div class="relative z-10">
				<div class="flex items-start justify-between mb-4">
					<div>
						<p class="text-indigo-200 text-sm font-medium">This Month</p>
						<h2 class="text-3xl font-black tracking-tight mt-1">{formatCurrency(group.thisMonth)}</h2>
					</div>
					<div class="h-12 w-12 rounded-2xl bg-surface-0/30 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
					</div>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div class="bg-surface-0/20 rounded-2xl p-3">
						<p class="text-xs text-indigo-200 font-medium">You are owed</p>
						<p class="text-lg font-bold text-emerald-300">{formatCurrency(totalOwed)}</p>
					</div>
					<div class="bg-surface-0/20 rounded-2xl p-3">
						<p class="text-xs text-indigo-200 font-medium">You owe</p>
						<p class="text-lg font-bold text-rose-300">{formatCurrency(totalOwing)}</p>
					</div>
				</div>
			</div>
		</section>

		<!-- Quick Actions -->
		<section class="grid grid-cols-2 gap-3">
			<a href="/split" class="h-20 rounded-2xl bg-surface-0 shadow-md border border-surface-200 p-4 flex flex-col items-center justify-center gap-2 active:scale-[0.98] transition-transform">
				<div class="h-10 w-10 rounded-xl bg-indigo-100 flex items-center justify-center">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-indigo-600"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
				</div>
				<span class="text-sm font-bold text-text-primary">New Split</span>
			</a>
			<a href="/receipt" class="h-20 rounded-2xl bg-surface-0 shadow-md border border-surface-200 p-4 flex flex-col items-center justify-center gap-2 active:scale-[0.98] transition-transform">
				<div class="h-10 w-10 rounded-xl bg-rose-100 flex items-center justify-center">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-rose-600"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
				</div>
				<span class="text-sm font-bold text-text-primary">Scan Receipt</span>
			</a>
		</section>

		<!-- Members -->
		<section>
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-sm font-bold text-text-primary">Members</h2>
				<span class="text-xs font-bold text-text-secondary">{group.members.length} people</span>
			</div>

			<div class="rounded-3xl bg-surface-0 shadow-md border border-surface-200 overflow-hidden">
				{#each group.members as member, index}
					<div class="p-4 flex items-center gap-3 {index < group.members.length - 1 ? 'border-b border-surface-100' : ''}">
						<div class="h-11 w-11 rounded-full bg-{member.color}-200 border-2 border-surface-0 flex items-center justify-center text-sm font-bold text-{member.color}-700 shrink-0 shadow-sm">
							{getInitials(member.name)}
						</div>
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2">
								<p class="text-sm font-bold text-text-primary truncate">{member.name}</p>
								{#if member.role === 'admin'}
									<span class="text-[10px] font-bold bg-surface-100 text-text-secondary px-1.5 py-0.5 rounded">Admin</span>
								{/if}
							</div>
							<p class="text-xs text-text-secondary truncate">{member.email}</p>
						</div>
						<div class="text-right">
							{#if member.balance > 0}
								<p class="text-sm font-bold text-emerald-600">+{formatCurrency(member.balance)}</p>
								<p class="text-[10px] text-text-tertiary">owed to you</p>
							{:else if member.balance < 0}
								<p class="text-sm font-bold text-rose-600">{formatCurrency(member.balance)}</p>
								<p class="text-[10px] text-text-tertiary">you owe</p>
							{:else}
								<p class="text-sm font-bold text-text-tertiary">Settled</p>
							{/if}
						</div>
					</div>
				{/each}

				<div class="p-3 bg-surface-50 border-t border-surface-100">
					<button type="button" class="w-full h-10 rounded-xl border-2 border-dashed border-surface-300 text-text-secondary font-bold text-sm flex items-center justify-center gap-2 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all active:scale-[0.99]">
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
						Invite Member
					</button>
				</div>
			</div>
		</section>

		<!-- Recent Receipts -->
		<section>
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-sm font-bold text-text-primary">Recent Receipts</h2>
				<a href="#" class="text-xs font-bold text-indigo-600">View all</a>
			</div>

			<div class="space-y-3">
				{#each group.receipts as receipt}
					<a href="/split/{receipt.id}" class="block rounded-2xl bg-surface-0 shadow-md border border-surface-200 p-4 active:scale-[0.99] transition-transform">
						<div class="flex items-center gap-3">
							<div class="h-12 w-12 rounded-2xl bg-{receipt.status === 'settled' ? 'emerald' : 'amber'}-100 flex items-center justify-center shrink-0">
								{#if receipt.status === 'settled'}
									<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-600"><path d="M20 6 9 12 15 15 9"/><path d="M20 6"/></svg>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-600"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 12 2"/></svg>
								{/if}
							</div>
							<div class="flex-1 min-w-0">
								<p class="text-sm font-bold text-text-primary truncate">{receipt.title}</p>
								<p class="text-xs text-text-secondary mt-0.5">{receipt.date} • Paid by {receipt.paidBy}</p>
							</div>
							<div class="text-right">
								<p class="text-sm font-bold text-text-primary">{formatCurrency(receipt.amount)}</p>
								<span class="text-[10px] font-bold {receipt.status === 'settled' ? 'text-emerald-600' : 'text-amber-600'} uppercase">{receipt.status}</span>
							</div>
						</div>
					</a>
				{/each}
			</div>
		</section>

		<!-- Send Reminder -->
		<section class="rounded-3xl bg-amber-50 border border-amber-200 p-4">
			<div class="flex items-start gap-3">
				<div class="h-10 w-10 rounded-2xl bg-surface-0 border border-amber-200 flex items-center justify-center shadow-sm">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-600"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
				</div>
				<div class="min-w-0 flex-1">
					<p class="text-sm font-bold text-text-primary">Payment Reminder</p>
					<p class="text-xs text-text-secondary mt-0.5">Send reminders to members with pending balances.</p>
					<a href="/send-reminder?group={groupId}" class="mt-2 inline-flex h-9 px-4 items-center justify-center rounded-xl bg-amber-500 text-white text-xs font-bold shadow-md active:scale-95 transition-transform">
						Send Reminders
					</a>
				</div>
			</div>
		</section>

		<!-- Settlement Summary -->
		<section class="rounded-3xl bg-surface-0 shadow-md border border-surface-200 overflow-hidden">
			<div class="px-5 py-3 border-b border-surface-100 bg-surface-50/50">
				<h2 class="text-sm font-bold text-text-primary">Settlement Summary</h2>
			</div>
			<div class="p-4 space-y-3">
				{#each group.members as member}
					{#if member.balance < 0}
						<div class="flex items-center justify-between p-3 bg-rose-50 rounded-xl border border-rose-100">
							<div class="flex items-center gap-2">
								<div class="h-8 w-8 rounded-full bg-{member.color}-200 flex items-center justify-center text-xs font-bold text-{member.color}-700">
									{getInitials(member.name)}
								</div>
								<span class="text-sm font-medium text-text-primary">{member.name}</span>
							</div>
							<div class="flex items-center gap-2">
								<span class="text-sm font-bold text-rose-600">{formatCurrency(Math.abs(member.balance))}</span>
								<button type="button" class="h-8 px-3 rounded-lg bg-rose-500 text-white text-xs font-bold active:scale-95 transition-transform">
									Settle
								</button>
							</div>
						</div>
					{:else if member.balance > 0 && member.id !== '1'}
						<div class="flex items-center justify-between p-3 bg-emerald-50 rounded-xl border border-emerald-100">
							<div class="flex items-center gap-2">
								<div class="h-8 w-8 rounded-full bg-{member.color}-200 flex items-center justify-center text-xs font-bold text-{member.color}-700">
									{getInitials(member.name)}
								</div>
								<span class="text-sm font-medium text-text-primary">{member.name} owes you</span>
							</div>
							<span class="text-sm font-bold text-emerald-600">{formatCurrency(member.balance)}</span>
						</div>
					{/if}
				{/each}
			</div>
		</section>
	</main>
</div>
