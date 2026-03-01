<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
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
	let errors = $state<Record<string, string>>({});

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

		// Check if there's receipt data from the receipt page
		const receiptData = receiptStore.getReceipt();
		if (receiptData && receiptData.items && receiptData.items.length > 0) {
			// Pre-populate the bill amount with the receipt total
			billAmount = receiptData.total * 1000; // Convert to IDR if needed

			// If tax was detected, add it
			if (receiptData.tax > 0) {
				tax = receiptData.tax * 1000;
			}
		}
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
		// Validate name length
		if (name.length > 50) {
			errors[`person-${index}`] = 'Name must be 50 characters or less';
			return;
		}
		errors[`person-${index}`] = '';
		people = people.map((p, i) => i === index ? { ...p, name } : p);
	}

	const estimatedTotal = $derived(billAmount + tax + tip);
	const personShare = $derived(Math.round(estimatedTotal / people.length));

	function validateForm(): boolean {
		errors = {};
		let isValid = true;

		// Validate bill amount
		if (billAmount <= 0) {
			errors.billAmount = 'Bill amount must be greater than 0';
			isValid = false;
		}

		// Validate tax
		if (tax < 0) {
			errors.tax = 'Tax cannot be negative';
			isValid = false;
		}

		// Validate tip
		if (tip < 0) {
			errors.tip = 'Tip cannot be negative';
			isValid = false;
		}

		// Validate people
		if (people.length < 2) {
			errors.people = 'At least 2 people are required';
			isValid = false;
		}

		// Validate person names
		people.forEach((person, index) => {
			if (!person.name.trim()) {
				errors[`person-${index}`] = 'Name is required';
				isValid = false;
			}
		});

		return isValid;
	}

	async function handleCalculateSplit() {
		// Validate form first
		if (!validateForm()) {
			alert('Please fix the errors before proceeding');
			return;
		}

		calculating = true;

		try {
			// Prepare the split data
			const splitData = {
				person_names: people.map(p => p.name),
				item_assignments: [], // Will be populated when item splitting is implemented
				tax_amount_input: tax,
				tip_amount_input: tip,
				split_evenly: splitMethod === 'equal',
				total_amount: billAmount
			};

			// Call the API to calculate the split
			const response = await splitsService.calculate(splitData);

			// Store the split ID for sharing
			const splitId = response.split_id;

			// Navigate to the split detail page
			await goto(`/split/${splitId}`);

		} catch (error) {
			console.error('Failed to calculate split:', error);
			alert('Failed to calculate split. Please try again.');
		} finally {
			calculating = false;
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
</script>

<svelte:head>
	<title>Create Split - Split Bill</title>
	<meta name="color-scheme" content="light" />
</svelte:head>

<div class="w-full min-h-dvh flex flex-col bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-sans">
	<header
		class="shrink-0 px-4 pb-2 z-10"
		style="padding-top: max(env(safe-area-inset-top), 3rem);"
	>
		<div class="flex items-center justify-between max-w-lg mx-auto">
			<a href="/" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-2xl bg-white dark:bg-slate-800 shadow-sm border border-slate-200 dark:border-slate-700 active:scale-95 transition-transform hover:bg-slate-50 dark:hover:bg-slate-700">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700 dark:text-slate-300"><path d="m15 18-6-6 6-6"/><path d="M18 6 6 18"/></svg>
			</a>
			<div class="text-center">
				<div class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">New Split</div>
				<h1 class="text-lg font-black tracking-tight text-slate-900 dark:text-white">Bill Details</h1>
			</div>
			<button type="button" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-2xl bg-white dark:bg-slate-800 shadow-sm border border-slate-200 dark:border-slate-700 active:scale-95 transition-transform" aria-label="More options">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700 dark:text-slate-300"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
			</button>
		</div>
	</header>

	<main class="flex-1 overflow-y-auto px-4 py-4 space-y-5 max-w-lg mx-auto w-full" style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 2rem);">
		<!-- Amounts Card -->
		<section class="rounded-3xl bg-white dark:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 overflow-hidden">
			<!-- Currency Selector Header -->
			<div class="px-5 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between bg-slate-50/50 dark:bg-slate-700/50">
				<span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Currency</span>
				<button type="button" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-600 border border-slate-200 dark:border-slate-500 shadow-sm text-sm font-bold text-slate-800 dark:text-white active:scale-95 transition-transform hover:bg-slate-50 dark:hover:bg-slate-500">
					<span class="text-lg">🇮🇩</span>
					<span>IDR (Rp)</span>
					<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m6 9 6 6 6-6"/></svg>
				</button>
			</div>

			<div class="p-5 space-y-5">
				<!-- Bill Amount -->
				<div>
					<label for="bill-amount" class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Bill Amount</label>
					<div class="relative group">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 font-bold text-lg">Rp</span>
						<input
							id="bill-amount"
							name="bill-amount"
							inputmode="numeric"
							bind:value={billAmount}
							min="0"
							class="h-14 w-full rounded-2xl border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 pl-12 pr-4 text-xl font-bold text-slate-900 dark:text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all placeholder:text-slate-300 dark:placeholder:text-slate-500 tabular-nums {errors.billAmount ? 'border-red-500' : ''}"
						/>
						{#if errors.billAmount}
							<p class="mt-1 text-xs text-red-600 dark:text-red-400">{errors.billAmount}</p>
						{/if}
					</div>
				</div>

				<!-- Tax Field -->
				<div>
					<div class="flex items-center justify-between mb-2">
						<label for="tax-amount" class="block text-sm font-bold text-slate-700 dark:text-slate-300">Tax</label>
						<button type="button" class="text-xs font-bold text-primary-600 dark:text-primary-400 flex items-center gap-1 hover:text-primary-700 dark:hover:text-primary-300 transition-colors bg-primary-50 dark:bg-primary-900/30 px-2 py-1 rounded-lg">
							<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m13 2-9 9h9l-9 9 9-9h-9l9-9-9 9z"/></svg>
							Auto-detect
						</button>
					</div>
					<div class="relative">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 font-bold">Rp</span>
						<input
							id="tax-amount"
							name="tax-amount"
							inputmode="numeric"
							bind:value={tax}
							placeholder="0"
							class="h-12 w-full rounded-2xl border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 pl-12 pr-4 text-base font-bold text-slate-900 dark:text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all tabular-nums"
						/>
					</div>
					<p class="mt-1.5 text-xs text-slate-400 dark:text-slate-500 font-medium">If not included in bill amount.</p>
				</div>

				<!-- Tip Section -->
				<div>
					<div class="flex items-center justify-between mb-2">
						<label for="tip-amount" class="block text-sm font-bold text-slate-700 dark:text-slate-300">Tip</label>
						<span class="text-xs font-bold text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded-full">OPTIONAL</span>
					</div>
					<div class="relative mb-3">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 font-bold">Rp</span>
						<input
							id="tip-amount"
							name="tip-amount"
							inputmode="numeric"
							bind:value={tip}
							class="h-12 w-full rounded-2xl border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 pl-12 pr-4 text-base font-bold text-slate-900 dark:text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all tabular-nums"
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
						<button type="button" class="h-10 rounded-xl bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 text-xs font-bold hover:bg-primary-50 dark:hover:bg-primary-900/30 hover:border-primary-200 hover:text-primary-700 dark:hover:text-primary-400 transition-colors">
							Custom
						</button>
					</div>
				</div>
			</div>

			<!-- Total Footer -->
			<div class="bg-slate-50 dark:bg-slate-700/50 px-5 py-4 border-t border-slate-200 dark:border-slate-600">
				<div class="flex items-end justify-between">
					<div class="text-sm font-bold text-slate-500 dark:text-slate-400">Estimated Total</div>
					<div class="text-2xl font-black text-slate-900 dark:text-white tracking-tight tabular-nums">{formatCurrency(estimatedTotal)}</div>
				</div>
			</div>
		</section>

		<!-- Smart Rounding Options -->
		<section class="rounded-3xl bg-white dark:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 p-5">
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-sm font-bold text-slate-900 dark:text-white">Smart Rounding</h2>
				<span class="text-xs font-bold text-primary-700 dark:text-primary-300 bg-primary-100 dark:bg-primary-900/30 px-2 py-0.5 rounded-lg">ACTIVE</span>
			</div>
			<div class="grid grid-cols-3 gap-1 p-1 bg-slate-100 dark:bg-slate-700 rounded-2xl mb-3">
				<button
					type="button"
					class="py-2.5 rounded-xl text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-600 hover:shadow-sm transition-all {roundingMode === 'down' ? 'bg-white dark:bg-slate-600 shadow-sm ring-1 ring-slate-200' : ''}"
					onclick={() => roundingMode = 'down'}
				>
					Down
				</button>
				<button
					type="button"
					class="py-2.5 rounded-xl text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-600 hover:shadow-sm transition-all {roundingMode === 'exact' ? 'bg-white dark:bg-slate-600 shadow-sm text-slate-900 dark:text-white ring-1 ring-slate-200' : ''}"
					onclick={() => roundingMode = 'exact'}
				>
					Exact
				</button>
				<button
					type="button"
					class="py-2.5 rounded-xl text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-600 hover:shadow-sm transition-all {roundingMode === 'up' ? 'bg-white dark:bg-slate-600 shadow-sm ring-1 ring-slate-200' : ''}"
					onclick={() => roundingMode = 'up'}
				>
					Up
				</button>
			</div>
			<div class="flex items-start gap-2.5 rounded-xl bg-slate-50 dark:bg-slate-700/50 border border-slate-100 dark:border-slate-600 p-3">
				<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-500 mt-0.5 shrink-0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
				<p class="text-xs text-slate-600 dark:text-slate-400 font-medium leading-relaxed">
					Total will be exactly <span class="font-bold text-slate-900 dark:text-white">{formatCurrency(estimatedTotal)}</span>. No rounding applied.
				</p>
			</div>
		</section>

		<!-- Split Style Tabs -->
		<section class="rounded-3xl bg-white dark:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 overflow-hidden">
			<div class="px-5 py-3 border-b border-slate-100 dark:border-slate-700">
				<h2 class="text-sm font-bold text-slate-900 dark:text-white">Split Method</h2>
			</div>
			<div class="p-5">
				<div class="grid grid-cols-3 gap-3 mb-4">
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl transition-all active:scale-[0.98] {splitMethod === 'equal' ? 'bg-primary-50 dark:bg-primary-900/30 border-2 border-primary-500 text-primary-700 dark:text-primary-300' : 'bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-500'}"
						onclick={() => splitMethod = 'equal'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M8 3H3v5"/><path d="M12 22v-8"/><path d="M12 15V9"/><path d="M12 9H4"/><path d="M12 9h8"/><path d="M16 21h5v-5"/><path d="M8 21H3v-5"/></svg>
						<span class="text-xs font-extrabold">Equal</span>
					</button>
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-500 transition-all active:scale-[0.98]"
						onclick={() => splitMethod = 'percentage'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>
						<span class="text-xs font-bold">% Split</span>
					</button>
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-500 transition-all active:scale-[0.98]"
						onclick={() => splitMethod = 'item'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
						<span class="text-xs font-bold">By Item</span>
					</button>
				</div>
				<div class="flex items-start gap-3">
					<div class="h-10 w-10 shrink-0 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
					</div>
					<div>
						<p class="text-sm font-bold text-slate-900 dark:text-white">Equal Split</p>
						<p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-0.5">We'll divide the total bill evenly between everyone added below.</p>
					</div>
				</div>
			</div>
		</section>

		<!-- People Manager -->
		<section class="rounded-3xl bg-white dark:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 overflow-hidden">
			<div class="px-5 py-3 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center">
				<h2 class="text-sm font-bold text-slate-900 dark:text-white">People</h2>
				<span class="bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2.5 py-0.5 rounded-lg text-xs font-bold">{people.length}</span>
			</div>
			<div class="p-5 space-y-4">
				{#each people as person, index}
					<div class="bg-slate-50 dark:bg-slate-700/50 rounded-2xl p-3 border border-slate-200 dark:border-slate-600">
						<div class="flex items-center gap-3 mb-3">
							<Avatar name={person.name} size="md" color={person.color || 'slate'} variant="solid" />
							<div class="flex-1 min-w-0">
								<label for="p{index}-name" class="sr-only">Person {index + 1} Name</label>
								<input
									id="p{index}-name"
									type="text"
									bind:value={person.name}
									maxlength="50"
									oninput={(e) => updatePersonName(index, e.currentTarget.value)}
									class="bg-transparent border-none p-0 text-sm font-bold text-slate-900 dark:text-white focus:ring-0 w-full {errors[`person-${index}`] ? 'text-red-600' : ''}"
								/>
								{#if errors[`person-${index}`]}
									<p class="text-xs text-red-600 dark:text-red-400">{errors[`person-${index}`]}</p>
								{:else}
									<div class="text-xs text-slate-500 dark:text-slate-400">{(100 / people.length).toFixed(1)}% share</div>
								{/if}
							</div>
							<button
								type="button"
								class="h-11 w-11 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg text-slate-400 hover:bg-rose-50 dark:hover:bg-rose-900/30 hover:text-rose-500 dark:hover:text-rose-400 transition-colors"
								aria-label="Remove {person.name}"
								onclick={() => removePerson(index)}
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
							</button>
						</div>

						<div class="flex items-center gap-2">
							<button
								type="button"
								class="flex-1 h-10 rounded-xl bg-white dark:bg-slate-600 border border-slate-200 dark:border-slate-500 shadow-sm text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center justify-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-500 active:scale-95 transition-all"
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="M12 5v14M5 12h14"/></svg>
								Assign Items
							</button>
							<div class="px-3 h-10 rounded-xl bg-white dark:bg-slate-600 border border-slate-200 dark:border-slate-500 flex items-center justify-center text-sm font-black text-slate-800 dark:text-white shadow-sm min-w-[90px] tabular-nums">
								{formatCurrency(personShare)}
							</div>
						</div>
					</div>
				{/each}

				<!-- Add Button -->
				<button
					type="button"
					class="w-full h-12 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-600 text-slate-500 dark:text-slate-400 font-bold text-sm flex items-center justify-center gap-2 hover:border-primary-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all active:scale-[0.99]"
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
				class="w-full h-14 rounded-2xl bg-primary-500 dark:bg-primary-600 text-white font-extrabold text-lg shadow-lg shadow-primary-500/30 dark:shadow-primary-900/50 flex items-center justify-center gap-2 active:scale-[0.98] transition-all"
				onclick={handleCalculateSplit}
			>
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
				Calculate Split
			</button>

			<button
				type="button"
				class="mt-3 w-full h-14 rounded-2xl bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-200 font-bold text-sm shadow-sm flex items-center justify-center gap-2 active:scale-[0.98] transition-all hover:bg-slate-50 dark:hover:bg-slate-600"
			>
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
				Save as Template
			</button>
		</section>
	</main>
</div>
