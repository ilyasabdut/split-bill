<script lang="ts">
	import { page } from '$app/stores';

	const groupId = $derived($page.url.searchParams.get('group'));

	const members = [
		{ id: '2', name: 'Sarah', email: 'sarah@email.com', color: 'emerald', balance: -85000, selected: true },
		{ id: '3', name: 'Mike', email: 'mike@email.com', color: 'rose', balance: -40000, selected: true },
		{ id: '4', name: 'Alex', email: 'alex@email.com', color: 'amber', balance: 0, selected: false },
	];

	let selectedMembers = $state(members.filter(m => m.selected));
	let customMessage = $state('');
	let isSending = $state(false);
	let sent = $state(false);

	const totalAmount = selectedMembers.reduce((sum, m) => sum + Math.abs(m.balance), 0);

	function toggleMember(id: string) {
		const member = members.find(m => m.id === id);
		if (member) {
			member.selected = !member.selected;
			selectedMembers = members.filter(m => m.selected);
		}
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

	async function handleSendReminder() {
		if (selectedMembers.length === 0) return;

		isSending = true;

		await new Promise(resolve => setTimeout(resolve, 1500));

		isSending = false;
		sent = true;
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
	<title>Send Reminder - Split Bill</title>
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
				<h1 class="text-lg font-black tracking-tight text-text-primary">Send Reminder</h1>
			</div>
			<div class="h-11 w-11"></div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="flex-1 overflow-y-auto px-4 py-4 space-y-5 max-w-lg mx-auto w-full" style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 2rem);">

		{#if sent}
			<!-- Success State -->
			<section class="pt-20 text-center" aria-label="Success confirmation">
				<div class="mx-auto h-24 w-24 rounded-full bg-emerald-100 flex items-center justify-center mb-6">
					<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-600"><path d="M20 6 9 12 15 15 9"/><path d="M20 6"/></svg>
				</div>
				<h2 class="text-2xl font-black text-text-primary">Reminders Sent!</h2>
				<p class="text-text-secondary mt-2">Email notifications have been sent to {selectedMembers.length} member{selectedMembers.length > 1 ? 's' : ''}.</p>

				<div class="mt-8 rounded-2xl bg-surface-0 shadow-md border border-surface-200 p-4 text-left">
					<p class="text-xs font-bold text-text-secondary uppercase tracking-wider mb-3">Recipients</p>
					{#each selectedMembers as member}
						<div class="flex items-center gap-3 py-2">
							<div class="h-8 w-8 rounded-full bg-{member.color}-200 flex items-center justify-center text-xs font-bold text-{member.color}-700">
								{getInitials(member.name)}
							</div>
							<div class="flex-1">
								<p class="text-sm font-medium text-text-primary">{member.name}</p>
								<p class="text-xs text-text-secondary">{member.email}</p>
							</div>
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-500"><path d="M22 2 11 13"/><path d="m22 2-7 20-4-9-9-4 20-7z"/></svg>
						</div>
					{/each}
				</div>

				<button
					type="button"
					onclick={handleBack}
					class="mt-6 w-full h-14 rounded-2xl bg-emerald-500 text-white font-extrabold text-lg shadow-lg shadow-emerald-500/30 active:scale-[0.98] transition-all"
				>
					Done
				</button>
			</section>
		{:else}
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
								<p class="text-xs text-text-secondary truncate">{member.email}</p>
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

			<!-- Preview Email -->
			<section class="rounded-3xl bg-surface-800 p-4 text-text-inverted">
				<div class="flex items-center gap-2 mb-3">
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
					<span class="text-xs font-bold text-text-tertiary uppercase tracking-wider">Email Preview</span>
				</div>
				<div class="bg-surface-0/20 rounded-2xl p-4 text-sm">
					<p class="font-bold text-text-inverted mb-2">Hi {"{name}"}!</p>
					<p class="text-text-tertiary leading-relaxed">
						You have a pending balance of <span class="text-amber-400 font-bold">{"{amount}"}</span> in our group "{groupId ? 'Roomies' : 'Split Bill'}".
						{customMessage ? `\n\n${customMessage}` : ''}
					</p>
					<p class="text-text-tertiary mt-3">Please settle up when you get a chance!</p>
				</div>
			</section>

			<!-- Action Buttons -->
			<section class="pt-2 space-y-3">
				<button
					type="button"
					onclick={handleSendReminder}
					disabled={isSending || selectedMembers.length === 0}
					class="w-full h-14 rounded-2xl bg-amber-500 text-white font-extrabold text-lg shadow-lg shadow-amber-500/30 flex items-center justify-center gap-2 active:scale-[0.98] transition-all disabled:opacity-60 disabled:cursor-not-allowed"
				>
					{#if isSending}
						<svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						Sending...
					{:else}
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4 20-7z"/></svg>
						Send {selectedMembers.length} Reminder{selectedMembers.length !== 1 ? 's' : ''}
					{/if}
				</button>

				<button
					type="button"
					onclick={handleBack}
					class="w-full h-12 rounded-2xl bg-surface-0 border border-surface-200 text-text-secondary font-bold text-sm shadow-sm flex items-center justify-center gap-2 active:scale-[0.98] transition-all hover:bg-surface-50"
				>
					Cancel
				</button>
			</section>
		{/if}
	</main>
</div>
