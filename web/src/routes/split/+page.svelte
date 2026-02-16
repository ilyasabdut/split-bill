<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { splitsService } from '$lib/services/api';
	import { receiptStore, splitStore, currencyStore, templatesStore, groupsStore } from '$lib/stores';
	import { calculateSplit } from '$lib/services/offline';
	import { offlineStore } from '$lib/stores/offline';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import Select from '$lib/components/ui/Select.svelte';

	interface Person {
		name: string;
		color?: 'indigo' | 'emerald' | 'rose' | 'amber' | 'sky' | 'violet' | 'slate';
	}

	let people = $state<Person[]>([
		{ name: 'Ava', color: 'indigo' },
		{ name: 'Ben', color: 'emerald' }
	]);
	let billAmount = $state(740000);
	let tax = $state(0);
	let tip = $state(50000);
	let calculating = $state(false);
	let selectedTip = $state(20);
	let roundingMode = $state<'down' | 'exact' | 'up'>('exact');
	let splitMethod = $state<'equal' | 'percentage' | 'item'>('equal');
	let selectedCurrency = $state('IDR');

	const currencies = [
		{ value: 'USD', label: 'USD ($)', icon: '🇺🇸' },
		{ value: 'IDR', label: 'IDR (Rp)', icon: '🇮🇩' },
		{ value: 'EUR', label: 'EUR (€)', icon: '🇪🇺' },
		{ value: 'JPY', label: 'JPY (¥)', icon: '🇯🇵' },
	];

	const quickTipOptions = [15, 18, 20];

	onMount(async () => {
		await Promise.all([
			currencyStore.init(),
			templatesStore.loadTemplates(),
			groupsStore.loadGroups()
		]);
	});

	function handleQuickTip(percentage: number) {
		selectedTip = percentage;
		tip = billAmount * (percentage / 100);
	}

	function addPerson() {
		const colors: Array<'indigo' | 'emerald' | 'rose' | 'amber' | 'sky' | 'violet' | 'slate'> =
			['indigo', 'emerald', 'rose', 'amber', 'sky', 'violet', 'slate'];
		const newPerson: Person = {
			name: `Person ${people.length + 1}`,
			color: colors[people.length % colors.length]
		};
		people = [...people, newPerson];
	}

	function removePerson(index: number) {
		people = people.filter((_, i) => i !== index);
	}

	function updatePersonName(index: number, name: string) {
		people = people.map((p, i) => i === index ? { ...p, name } : p);
	}

	const estimatedTotal = $derived(billAmount + tax + tip);
	const personShare = $derived(Math.round(estimatedTotal / people.length));

	async function handleCalculateSplit() {
		calculating = true;
		// Implementation here
		setTimeout(() => {
			calculating = false;
		}, 1000);
	}

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}
</script>

<svelte:head>
	<title>Create Split - Split Bill</title>
	<meta name="color-scheme" content="light" />
</svelte:head>

<div class="w-full h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
	<!-- Header (safe area) -->
	<header class="shrink-0 pt-12 px-4 pb-2 z-10">
		<div class="flex items-center justify-between">
			<a href="/" class="h-11 w-11 inline-flex items-center justify-center rounded-2xl bg-white shadow-sm border border-slate-200 active:scale-95 transition-transform">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700"><path d="m15 18-6-6 6-6"/><path d="M18 6 6 18"/></svg>
			</a>
			<div class="text-center">
				<div class="text-xs font-bold text-slate-500 uppercase tracking-wider">New Split</div>
				<h1 class="text-lg font-black tracking-tight text-slate-900">Bill Details</h1>
			</div>
			<button type="button" class="h-11 w-11 inline-flex items-center justify-center rounded-2xl bg-white shadow-sm border border-slate-200 active:scale-95 transition-transform" aria-label="More options">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
			</button>
		</div>
	</header>

	<!-- Main Scrollable Area -->
	<main class="flex-1 overflow-y-auto px-4 py-4 pb-[120px] space-y-5">
		<!-- Amounts Card -->
		<section class="rounded-3xl bg-white shadow-md border border-slate-200 overflow-hidden">
			<!-- Currency Selector Header -->
			<div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
				<span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Currency</span>
				<button type="button" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-slate-200 shadow-sm text-sm font-bold text-slate-800 active:scale-95 transition-transform hover:bg-slate-50">
					<span class="text-lg">🇮🇩</span>
					<span>IDR (Rp)</span>
					<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m6 9 6 6 6-6"/></svg>
				</button>
			</div>

			<div class="p-5 space-y-5">
				<!-- Bill Amount -->
				<div>
					<label for="bill-amount" class="block text-sm font-bold text-slate-700 mb-2">Bill Amount</label>
					<div class="relative group">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-lg">Rp</span>
						<input
							id="bill-amount"
							name="bill-amount"
							inputmode="numeric"
							bind:value={billAmount}
							class="h-14 w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-xl font-bold text-slate-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all placeholder:text-slate-300 tabular-nums"
						/>
					</div>
				</div>

				<!-- Tax Field -->
				<div>
					<div class="flex items-center justify-between mb-2">
						<label for="tax-amount" class="block text-sm font-bold text-slate-700">Tax</label>
						<button type="button" class="text-xs font-bold text-primary-600 flex items-center gap-1 hover:text-primary-700 transition-colors bg-primary-50 px-2 py-1 rounded-lg">
							<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m13 2-9 9h9l-9 9 9-9h-9l9-9-9 9z"/></svg>
							Auto-detect
						</button>
					</div>
					<div class="relative">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold">Rp</span>
						<input
							id="tax-amount"
							name="tax-amount"
							inputmode="numeric"
							bind:value={tax}
							placeholder="0"
							class="h-12 w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-base font-bold text-slate-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all tabular-nums"
						/>
					</div>
					<p class="mt-1.5 text-xs text-slate-400 font-medium">If not included in bill amount.</p>
				</div>

				<!-- Tip Section -->
				<div>
					<div class="flex items-center justify-between mb-2">
						<label for="tip-amount" class="block text-sm font-bold text-slate-700">Tip</label>
						<span class="text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">OPTIONAL</span>
					</div>
					<div class="relative mb-3">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold">Rp</span>
						<input
							id="tip-amount"
							name="tip-amount"
							inputmode="numeric"
							bind:value={tip}
							class="h-12 w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-base font-bold text-slate-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all tabular-nums"
						/>
					</div>

					<!-- Quick Tip Grid -->
					<div class="grid grid-cols-4 gap-2">
						{#each quickTipOptions as percent}
							<button
								type="button"
								class="h-10 rounded-xl text-xs font-bold transition-colors"
								class:bg-slate-50={selectedTip !== percent}
								class:border-slate-200={selectedTip !== percent}
								class:text-slate-600={selectedTip !== percent}
								class:hover:bg-primary-50={selectedTip !== percent}
								class:hover:border-primary-200={selectedTip !== percent}
								class:hover:text-primary-700={selectedTip !== percent}
								class:bg-primary-500={selectedTip === percent}
								class:border-primary-600={selectedTip === percent}
								class:text-white={selectedTip === percent}
								class:shadow-sm={selectedTip === percent}
								class:ring-2={selectedTip === percent}
								class:ring-primary-100={selectedTip === percent}
								class:ring-offset-1={selectedTip === percent}
								onclick={() => handleQuickTip(percent)}
							>
								{percent}%
							</button>
						{/each}
						<button type="button" class="h-10 rounded-xl bg-slate-50 border border-slate-200 text-slate-600 text-xs font-bold hover:bg-primary-50 hover:border-primary-200 hover:text-primary-700 transition-colors">
							Custom
						</button>
					</div>
				</div>
			</div>

			<!-- Total Footer -->
			<div class="bg-slate-50 px-5 py-4 border-t border-slate-200">
				<div class="flex items-end justify-between">
					<div class="text-sm font-bold text-slate-500">Estimated Total</div>
					<div class="text-2xl font-black text-slate-900 tracking-tight tabular-nums">{formatCurrency(estimatedTotal)}</div>
				</div>
			</div>
		</section>

		<!-- Smart Rounding Options -->
		<section class="rounded-3xl bg-white shadow-md border border-slate-200 p-5">
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-sm font-bold text-slate-900">Smart Rounding</h2>
				<span class="text-[10px] font-bold text-primary-700 bg-primary-100 px-2 py-0.5 rounded-lg">ACTIVE</span>
			</div>
			<div class="grid grid-cols-3 gap-1 p-1 bg-slate-100 rounded-2xl mb-3">
				<button
					type="button"
					class="py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-white hover:shadow-sm transition-all"
					class:bg-white={roundingMode === 'down'}
					class:shadow-sm={roundingMode === 'down'}
					class:ring-1={roundingMode === 'down'}
					class:ring-slate-200={roundingMode === 'down'}
					onclick={() => roundingMode = 'down'}
				>
					Down
				</button>
				<button
					type="button"
					class="py-2.5 rounded-xl text-xs font-bold"
					class:text-slate-600={roundingMode !== 'exact'}
					class:hover:bg-white={roundingMode !== 'exact'}
					class:hover:shadow-sm={roundingMode !== 'exact'}
					class:transition-all={roundingMode !== 'exact'}
					class:bg-white={roundingMode === 'exact'}
					class:shadow-sm={roundingMode === 'exact'}
					class:text-slate-900={roundingMode === 'exact'}
					class:ring-1={roundingMode === 'exact'}
					class:ring-slate-200={roundingMode === 'exact'}
					onclick={() => roundingMode = 'exact'}
				>
					Exact
				</button>
				<button
					type="button"
					class="py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-white hover:shadow-sm transition-all"
					class:bg-white={roundingMode === 'up'}
					class:shadow-sm={roundingMode === 'up'}
					class:ring-1={roundingMode === 'up'}
					class:ring-slate-200={roundingMode === 'up'}
					onclick={() => roundingMode = 'up'}
				>
					Up
				</button>
			</div>
			<div class="flex items-start gap-2.5 rounded-xl bg-slate-50 border border-slate-100 p-3">
				<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-500 mt-0.5 shrink-0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
				<p class="text-xs text-slate-600 font-medium leading-relaxed">
					Total will be exactly <span class="font-bold text-slate-900">{formatCurrency(estimatedTotal)}</span>. No rounding applied.
				</p>
			</div>
		</section>

		<!-- Split Style Tabs -->
		<section class="rounded-3xl bg-white shadow-md border border-slate-200 overflow-hidden">
			<div class="px-5 py-3 border-b border-slate-100">
				<h2 class="text-sm font-bold text-slate-900">Split Method</h2>
			</div>
			<div class="p-5">
				<div class="grid grid-cols-3 gap-3 mb-4">
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl transition-all active:scale-[0.98]"
						class:bg-primary-50={splitMethod === 'equal'}
						class:border-2={splitMethod === 'equal'}
						class:border-primary-500={splitMethod === 'equal'}
						class:text-primary-700={splitMethod === 'equal'}
						class:bg-white={splitMethod !== 'equal'}
						class:border={splitMethod !== 'equal'}
						class:border-slate-200={splitMethod !== 'equal'}
						class:text-slate-600={splitMethod !== 'equal'}
						class:hover:border-slate-300={splitMethod !== 'equal'}
						onclick={() => splitMethod = 'equal'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M8 3H3v5"/><path d="M12 22v-8"/><path d="M12 15V9"/><path d="M12 9H4"/><path d="M12 9h8"/><path d="M16 21h5v-5"/><path d="M8 21H3v-5"/></svg>
						<span class="text-xs font-extrabold">Equal</span>
					</button>
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl bg-white border border-slate-200 text-slate-600 hover:border-slate-300 transition-all active:scale-[0.98]"
						onclick={() => splitMethod = 'percentage'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>
						<span class="text-xs font-bold">% Split</span>
					</button>
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl bg-white border border-slate-200 text-slate-600 hover:border-slate-300 transition-all active:scale-[0.98]"
						onclick={() => splitMethod = 'item'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
						<span class="text-xs font-bold">By Item</span>
					</button>
				</div>
				<div class="flex items-start gap-3">
					<div class="h-10 w-10 shrink-0 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
					</div>
					<div>
						<p class="text-sm font-bold text-slate-900">Equal Split</p>
						<p class="text-xs text-slate-500 leading-relaxed mt-0.5">We'll divide the total bill evenly between everyone added below.</p>
					</div>
				</div>
			</div>
		</section>

		<!-- People Manager -->
		<section class="rounded-3xl bg-white shadow-md border border-slate-200 overflow-hidden">
			<div class="px-5 py-3 border-b border-slate-100 flex justify-between items-center">
				<h2 class="text-sm font-bold text-slate-900">People</h2>
				<span class="bg-slate-100 text-slate-600 px-2.5 py-0.5 rounded-lg text-xs font-bold">{people.length}</span>
			</div>
			<div class="p-5 space-y-4">
				{#each people as person, index}
					<div class="bg-slate-50 rounded-2xl p-3 border border-slate-200">
						<div class="flex items-center gap-3 mb-3">
							<Avatar name={person.name} size="md" color={person.color || 'slate'} variant="solid" />
							<div class="flex-1 min-w-0">
								<label for="p{index}-name" class="sr-only">Person {index + 1} Name</label>
								<input
									id="p{index}-name"
									type="text"
									bind:value={person.name}
									class="bg-transparent border-none p-0 text-sm font-bold text-slate-900 focus:ring-0 w-full"
								/>
								<div class="text-xs text-slate-500">{(100 / people.length).toFixed(1)}% share</div>
							</div>
							<button
								type="button"
								class="h-8 w-8 flex items-center justify-center rounded-lg text-slate-400 hover:bg-rose-50 hover:text-rose-500 transition-colors"
								aria-label="Remove {person.name}"
								onclick={() => removePerson(index)}
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
							</button>
						</div>

						<div class="flex items-center gap-2">
							<button
								type="button"
								class="flex-1 h-10 rounded-xl bg-white border border-slate-200 shadow-sm text-xs font-bold text-slate-700 flex items-center justify-center gap-2 hover:bg-slate-50 active:scale-95 transition-all"
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="M12 5v14M5 12h14"/></svg>
								Assign Items
							</button>
							<div class="px-3 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-sm font-black text-slate-800 shadow-sm min-w-[90px] tabular-nums">
								{formatCurrency(personShare)}
							</div>
						</div>
					</div>
				{/each}

				<!-- Add Button -->
				<button
					type="button"
					class="w-full h-12 rounded-2xl border-2 border-dashed border-slate-300 text-slate-500 font-bold text-sm flex items-center justify-center gap-2 hover:border-primary-300 hover:text-primary-600 hover:bg-primary-50 transition-all active:scale-[0.99]"
					onclick={addPerson}
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
					Add Person
				</button>
			</div>
		</section>

		<!-- Action Area -->
		<section class="pt-2">
			<button
				type="button"
				class="w-full h-14 rounded-2xl bg-primary-500 text-white font-extrabold text-lg shadow-lg shadow-primary-500/30 flex items-center justify-center gap-2 active:scale-[0.98] transition-all"
				onclick={handleCalculateSplit}
			>
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
				Calculate Split
			</button>

			<button
				type="button"
				class="mt-3 w-full h-14 rounded-2xl bg-white border border-slate-200 text-slate-700 font-bold text-sm shadow-sm flex items-center justify-center gap-2 active:scale-[0.98] transition-all hover:bg-slate-50"
			>
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
				Save as Template
			</button>
		</section>
	</main>
</div>
