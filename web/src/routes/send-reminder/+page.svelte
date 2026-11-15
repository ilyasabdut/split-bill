<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';

	const groupId = $derived($page.url.searchParams.get('group'));

	type Member = { id: string; name: string; email: string; color: string; balance: number; selected: boolean };
	let members = $state<Member[]>([]);
	const colors = ['emerald', 'rose', 'amber', 'sky', 'violet'];

	// Who still owes: everyone but the payer (first person) on this device's unpaid splits
	onMount(async () => {
		const db = await getIndexedDB();
		const owed = new Map<string, number>();
		for (const split of await db.getAll<any>(STORES.SPLITS)) {
			const names = Object.keys(split.results || {});
			for (const name of names.slice(1)) {
				if (split.payments?.[name] === 'paid') continue;
				owed.set(name, (owed.get(name) || 0) + (split.results[name]?.total || 0));
			}
		}
		members = [...owed].filter(([, amount]) => amount > 0).map(([name, amount], i) => ({
			id: name, name, email: '', color: colors[i % colors.length], balance: -amount, selected: true
		}));
	});

	let customMessage = $state('');
	let copied = $state(false);

	const selectedMembers = $derived(members.filter(m => m.selected));
	const totalAmount = $derived(selectedMembers.reduce((sum, m) => sum + Math.abs(m.balance), 0));
	const reminderText = $derived(
		[
			'Hi! A reminder about our split bills:',
			...selectedMembers.map(m => `${m.name}: ${formatCurrency(Math.abs(m.balance))}`),
			customMessage.trim(),
			'Please settle up when you get a chance!'
		].filter(Boolean).join('\n')
	);

	function toggleMember(id: string) {
		const member = members.find(m => m.id === id);
		if (member) member.selected = !member.selected;
	}

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

	// Nothing is sent from here: the reminder goes out through the user's own apps
	async function handleShareReminder() {
		if (selectedMembers.length === 0) return;

		if (navigator.share) {
			try {
				await navigator.share({ title: 'Split Bill reminder', text: reminderText });
			} catch {
				// Share sheet dismissed
			}
			return;
		}

		await navigator.clipboard.writeText(reminderText);
		copied = true;
		setTimeout(() => copied = false, 2000);
	}

	function handleBack() {
		if (groupId) {
			window.location.href = `/groups/${groupId}`;
		} else {
			window.location.href = '/';
		}
	}
</script>

<svelte:head>
	<title>Share Reminder - Split Bill</title>
	<meta name="color-scheme" content="light" />
</svelte:head>

<div class="w-full min-h-dvh flex flex-col bg-surface-50 text-text-primary font-sans">
	<!-- Decorative background -->
	<div class="pointer-events-none absolute inset-0 overflow-hidden -z-10">
		<div class="absolute -top-24 -right-20 h-72 w-72 rounded-full bg-amber-500/15 blur-2xl"></div>
		<div class="absolute top-28 -left-24 h-72 w-72 rounded-full bg-rose-400/10 blur-2xl"></div>
	</div>

	<!-- Header -->
	<header class="shrink-0 px-4" style="padding-top: max(env(safe-area-inset-top), 3rem);">
		<div class="flex items-center justify-between max-w-lg mx-auto">
			<button type="button" onclick={handleBack} class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-2xl bg-surface-0 shadow-md border border-surface-200 active:scale-95 transition-transform hover:bg-surface-50" aria-label="Go back">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="m15 18-6-6 6-6"/><path d="M18 6 6 18"/></svg>
			</button>
			<div class="text-center">
				<div class="text-xs font-bold text-text-secondary uppercase tracking-wider">Payment</div>
				<h1 class="text-lg font-black tracking-tight text-text-primary">Share Reminder</h1>
			</div>
			<div class="h-11 w-11"></div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="flex-1 overflow-y-auto px-4 py-4 space-y-5 max-w-lg mx-auto w-full" style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 2rem);">

			<!-- Amount Summary -->
			<section class="rounded-2xl bg-amber-600 shadow-xl p-5 text-white relative overflow-hidden" aria-label="Amount summary">
				<div class="absolute right-0 top-0 h-40 w-40 bg-surface-0/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>

				<div class="relative z-10">
					<div class="flex items-center gap-2 mb-2">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
						<span class="text-sm font-medium text-amber-100">Total to collect</span>
					</div>
					<h2 class="text-3xl font-black tracking-tight">{formatCurrency(totalAmount)}</h2>
					<p class="text-sm text-amber-100 mt-2">from {selectedMembers.length} member{selectedMembers.length !== 1 ? 's' : ''}</p>
				</div>
			</section>

			<!-- Select Recipients -->
			<section>
				<h2 class="text-sm font-bold text-text-primary mb-3">Select Recipients</h2>
				<div class="rounded-xl bg-surface-0 shadow-md border border-surface-200 overflow-hidden">
					{#each members as member, index}
						<button
							type="button"
							onclick={() => toggleMember(member.id)}
							class="w-full p-4 flex items-center gap-3 text-left {index < members.length - 1 ? 'border-b border-surface-100' : ''} {member.balance === 0 ? 'opacity-50' : ''}"
							disabled={member.balance === 0}
						>
							<div class="h-11 w-11 rounded-full bg-{member.color}-200 border-2 border-surface-0 flex items-center justify-center text-sm font-bold text-{member.color}-700 shrink-0 shadow-sm">
								{getInitials(member.name)}
							</div>
							<div class="flex-1 min-w-0">
								<p class="text-sm font-bold text-text-primary">{member.name}</p>
							</div>
							{#if member.balance < 0}
								<div class="text-right">
									<p class="text-sm font-bold text-rose-600">{formatCurrency(Math.abs(member.balance))}</p>
									<p class="text-[10px] text-text-tertiary">owes you</p>
								</div>
								<div class="h-6 w-6 rounded-full {member.selected ? 'bg-amber-500' : 'bg-surface-200'} flex items-center justify-center transition-colors">
									{#if member.selected}
										<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white"><path d="M20 6 9 12 15 15 9"/><path d="M20 6"/></svg>
									{/if}
								</div>
							{:else}
								<span class="text-xs font-medium text-text-tertiary">Settled</span>
							{/if}
						</button>
					{:else}
						<p class="p-4 text-sm text-text-secondary">Nobody owes you right now.</p>
					{/each}
				</div>
			</section>

			<!-- Custom Message -->
			<section>
				<h2 class="text-sm font-bold text-text-primary mb-3">Custom Message <span class="text-text-tertiary font-normal">(optional)</span></h2>
				<div class="rounded-3xl bg-surface-0 shadow-md border border-surface-200 p-4">
					<textarea
						bind:value={customMessage}
						placeholder="Add a personal note to the reminder..."
						rows="3"
						class="w-full bg-transparent border-none p-0 text-sm text-text-primary focus:ring-0 placeholder:text-text-tertiary resize-none"
					></textarea>
				</div>
			</section>

			<!-- Reminder Preview -->
			<section class="rounded-3xl bg-surface-800 p-4 text-text-inverted">
				<div class="flex items-center gap-2 mb-3">
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
					<span class="text-xs font-bold text-text-tertiary uppercase tracking-wider">Reminder Preview</span>
				</div>
				<p class="bg-surface-0/20 rounded-2xl p-4 text-sm text-text-inverted leading-relaxed whitespace-pre-line">{reminderText}</p>
			</section>

			<!-- Action Buttons -->
			<section class="pt-2 space-y-3">
				<button
					type="button"
					onclick={handleShareReminder}
					disabled={selectedMembers.length === 0}
					class="w-full h-14 rounded-2xl bg-amber-500 text-white font-extrabold text-lg shadow-lg shadow-amber-500/30 flex items-center justify-center gap-2 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed"
				>
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4 20-7z"/></svg>
						{copied ? 'Copied to clipboard' : 'Share reminder'}
				</button>

				<button
					type="button"
					onclick={handleBack}
					class="w-full h-12 rounded-2xl bg-surface-0 border border-surface-200 text-text-secondary font-bold text-sm shadow-sm flex items-center justify-center gap-2 active:scale-[0.98] transition-all hover:bg-surface-50"
				>
					Cancel
				</button>
			</section>
	</main>
</div>
