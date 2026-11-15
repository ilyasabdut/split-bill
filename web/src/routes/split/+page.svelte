<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { splitsService, templatesService } from '$lib/services/api';
	import { receiptStore, currencyStore, templatesStore, groupsStore } from '$lib/stores';
	import type { CurrencyCode } from '$lib/stores/currency';
	import type { SplitResults } from '$lib/types/split';
	import { calculateSplit } from '$lib/services/offline/calc';
	import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import CurrencySelector from '$lib/components/CurrencySelector.svelte';

	interface Person {
		name: string;
		color?: 'indigo' | 'emerald' | 'rose' | 'amber' | 'sky' | 'violet' | 'slate';
	}

	let people = $state<Person[]>([
		{ name: 'Ava', color: 'indigo' },
		{ name: 'Ben', color: 'emerald' }
	]);
	let billAmount = $state(0);
	let tax = $state(0);
	let tip = $state(0);
	let calculating = $state(false);
	let selectedTip = $state<number | 'custom'>(20);
	let roundingMode = $state<'down' | 'exact' | 'up'>('exact');
	let splitMethod = $state<'equal' | 'percentage' | 'item'>('equal');
	let selectedCurrency = $state<CurrencyCode>('IDR');
	let errors = $state<Record<string, string>>({});
	let percentages = $state<number[]>([50, 50]);
	let receiptItems = $state<{ name: string; price: number; assignedTo: number[] }[]>([]);

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
		const receiptData = receiptStore.getReceipt() as import('$lib/types/receipt').ReceiptData | null;
		if (receiptData && receiptData.items && receiptData.items.length > 0) {
			// Pre-populate the bill amount with the receipt total
			// The receipt total already includes tax; the bill amount here is before tax
			tax = receiptData.tax && receiptData.tax > 0 ? receiptData.tax : 0;
			billAmount = (receiptData.total || 0) - tax;

			// Populate receipt items for "By Item" split
			receiptItems = receiptData.items.map(item => ({
				name: item.name || 'Item',
				price: item.price || 0,
				assignedTo: []
			}));
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
		const equalShare = Math.floor(100 / people.length);
		percentages = people.map((_, i) => i === people.length - 1 ? 100 - equalShare * (people.length - 1) : equalShare);
	}

	function removePerson(index: number) {
		people = people.filter((_, i) => i !== index);
		percentages = percentages.filter((_, i) => i !== index);
		const total = percentages.reduce((s, p) => s + p, 0);
		if (total !== 100 && percentages.length > 0) {
			percentages[0] += 100 - total;
			percentages = [...percentages];
		}
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

	function toggleItemAssignment(itemIndex: number, personIndex: number) {
		const item = receiptItems[itemIndex];
		const idx = item.assignedTo.indexOf(personIndex);
		if (idx >= 0) {
			item.assignedTo = item.assignedTo.filter(i => i !== personIndex);
		} else {
			item.assignedTo = [...item.assignedTo, personIndex];
		}
		receiptItems = [...receiptItems];
	}

	const estimatedTotal = $derived(billAmount + tax + tip);

	// Single source of split math: the preview and the saved split both use this
	const shares = $derived(calculateSplit({
		peopleCount: people.length,
		billAmount,
		tax,
		tip,
		method: splitMethod,
		percentages,
		items: receiptItems,
		rounding: roundingMode
	}));
	const percentageTotal = $derived(percentages.reduce((s, p) => s + p, 0));

	function validateForm(): boolean {
		errors = {};
		let isValid = true;

		if (billAmount <= 0) {
			errors.billAmount = 'Bill amount must be greater than 0';
			isValid = false;
		}

		if (tax < 0) {
			errors.tax = 'Tax cannot be negative';
			isValid = false;
		}

		if (tip < 0) {
			errors.tip = 'Tip cannot be negative';
			isValid = false;
		}

		if (people.length < 2) {
			errors.people = 'At least 2 people are required';
			isValid = false;
		}

		people.forEach((person, index) => {
			if (!person.name.trim()) {
				errors[`person-${index}`] = 'Name is required';
				isValid = false;
			}
		});

		if (splitMethod === 'percentage' && percentageTotal !== 100) {
			errors.percentages = 'Percentages must add up to 100%';
			isValid = false;
		}

		return isValid;
	}

	async function handleCalculateSplit() {
		if (!validateForm()) {
			alert('Please fix the errors before proceeding');
			return;
		}

		calculating = true;

		try {
			const results: SplitResults = Object.fromEntries(
				people.map((person, i) => [person.name, shares[i]])
			);

			const splitData = {
				person_names: people.map(p => p.name),
				item_assignments: [],
				tax_amount_input: tax,
				tip_amount_input: tip,
				split_evenly: splitMethod === 'equal',
				total_amount: billAmount,
				percentages: splitMethod === 'percentage' ? percentages : undefined,
				client_results: results
			};

			// The API only persists the split for sharing; offline it stays on this device
			let splitId: string;
			try {
				splitId = (await splitsService.calculate(splitData)).split_id;
			} catch {
				splitId = crypto.randomUUID();
			}

			const indexedDB = await getIndexedDB();
			await indexedDB.put(STORES.SPLITS, {
				id: splitId,
				results,
				createdAt: Date.now(),
				people: people.map(p => p.name),
				total: estimatedTotal,
				currency: selectedCurrency,
				status: 'unpaid'
			});

			await goto(`/split/${splitId}`);

		} catch (error) {
			console.error('Failed to calculate split:', error);
			alert('Failed to calculate split. Please try again.');
		} finally {
			calculating = false;
		}
	}

	async function handleSaveTemplate() {
		if (people.length < 2) {
			alert('Add at least 2 people to save a template');
			return;
		}

		const name = prompt('Template name:');
		if (!name?.trim()) return;

		const config = {
			people: people.map(p => p.name),
			splitMethod,
			percentages: splitMethod === 'percentage' ? percentages : undefined,
			currency: selectedCurrency
		};

		try {
			await templatesService.createTemplate({ name: name.trim(), config });
			alert('Template saved!');
		} catch {
			try {
				const indexedDB = await getIndexedDB();
				await indexedDB.put(STORES.TEMPLATES, {
					id: crypto.randomUUID(),
					name: name.trim(),
					createdAt: Date.now(),
					...config
				});
				alert('Template saved locally!');
			} catch {
				alert('Failed to save template.');
			}
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

<div class="w-full min-h-dvh flex flex-col bg-surface-50 text-text-primary font-sans">
	<header
		class="shrink-0 px-4 pb-2 z-10"
		style="padding-top: max(env(safe-area-inset-top), 3rem);"
	>
		<div class="flex items-center justify-between max-w-lg mx-auto">
			<a href="/" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-2xl bg-surface-0 dark:bg-surface-800 shadow-sm border border-surface-200 active:scale-95 transition-transform hover:bg-surface-100 dark:hover:bg-surface-700" aria-label="Go back home">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="m15 18-6-6 6-6"/><path d="M18 6 6 18"/></svg>
			</a>
			<div class="text-center">
				<div class="text-caption font-bold text-text-tertiary uppercase tracking-wider">New Split</div>
				<h1 class="text-subheading font-black tracking-tight text-text-primary">Bill Details</h1>
			</div>
			<button type="button" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-2xl bg-surface-0 dark:bg-surface-800 shadow-sm border border-surface-200 active:scale-95 transition-transform" aria-label="More options">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
			</button>
		</div>
	</header>

	<main class="flex-1 overflow-y-auto px-4 py-4 space-y-section max-w-lg mx-auto w-full" style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 2rem);">
		<!-- Amounts Card -->
		<section class="rounded-2xl bg-surface-0 shadow-card border border-surface-200 overflow-hidden animate-slide-up">
			<!-- Currency Selector Header -->
			<div class="px-5 py-3 border-b border-surface-100 flex items-center justify-between bg-surface-50/50">
				<span class="text-caption font-bold text-text-tertiary uppercase tracking-wider">Currency</span>
				<CurrencySelector selected={selectedCurrency} onChange={(c) => selectedCurrency = c} class="px-3 py-1.5 rounded-xl bg-surface-0 border border-surface-200 shadow-sm text-label font-bold text-text-primary active:scale-95 transition-transform hover:bg-surface-100" />
			</div>

			<div class="p-5 space-y-section">
				<!-- Bill Amount -->
				<div>
					<label for="bill-amount" class="block text-label font-bold text-text-primary mb-2">Bill Amount</label>
					<div class="relative group">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-text-tertiary font-bold text-lg">Rp</span>
						<input
							id="bill-amount"
							type="text"
							inputmode="numeric"
							bind:value={billAmount}
							placeholder="0"
							aria-invalid={!!errors.billAmount}
							aria-describedby="bill-amount-error"
							class="h-14 w-full rounded-2xl border border-surface-200 bg-surface-50 pl-12 pr-4 text-section font-bold text-text-primary shadow-sm focus-visible:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all placeholder:text-text-tertiary tabular-nums {errors.billAmount ? 'border-error' : ''}"
						/>
						{#if errors.billAmount}
							<p id="bill-amount-error" class="mt-1 text-caption text-error" role="alert">{errors.billAmount}</p>
						{/if}
					</div>
				</div>

				<!-- Tax Field -->
				<div>
					<div class="flex items-center justify-between mb-2">
						<label for="tax-amount" class="block text-label font-bold text-text-primary">Tax</label>
						<button type="button" class="text-caption font-bold text-primary-500 flex items-center gap-1 hover:text-primary-600 transition-colors bg-primary-50 px-2 py-1 rounded-lg" onclick={() => tax = Math.round(billAmount * 0.11)}>
							<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m13 2-9 9h9l-9 9 9-9h-9l9-9-9 9z"/></svg>
							Auto-detect
						</button>
					</div>
					<div class="relative">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-text-tertiary font-bold">Rp</span>
						<input
							id="tax-amount"
							name="tax-amount"
							inputmode="numeric"
							bind:value={tax}
							placeholder="0"
							class="h-12 w-full rounded-2xl border border-surface-200 bg-surface-50 pl-12 pr-4 text-body font-bold text-text-primary shadow-sm focus-visible:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all tabular-nums"
						/>
					</div>
					<p class="mt-1.5 text-caption text-text-tertiary font-medium">If not included in bill amount.</p>
				</div>

				<!-- Tip Section -->
				<div>
					<div class="flex items-center justify-between mb-2">
						<label for="tip-amount" class="block text-label font-bold text-text-primary">Tip</label>
						<span class="text-caption font-bold text-text-tertiary bg-surface-100 px-2 py-0.5 rounded-full">OPTIONAL</span>
					</div>
					<div class="relative mb-3">
						<span class="absolute left-4 top-1/2 -translate-y-1/2 text-text-tertiary font-bold">Rp</span>
						<input
							id="tip-amount"
							name="tip-amount"
							inputmode="numeric"
							bind:value={tip}
							class="h-12 w-full rounded-2xl border border-surface-200 bg-surface-50 pl-12 pr-4 text-body font-bold text-text-primary shadow-sm focus-visible:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all tabular-nums"
						/>
					</div>

					<!-- Quick Tip Grid -->
					<div class="grid grid-cols-4 gap-2">
						{#each quickTipOptions as percent}
							<button
								type="button"
								class="h-10 rounded-xl text-caption font-bold transition-all duration-200 hover:scale-105 active:scale-95"
								class:bg-surface-50={selectedTip !== percent}
								class:border-surface-200={selectedTip !== percent}
								class:text-text-secondary={selectedTip !== percent}
								class:hover:bg-primary-50={selectedTip !== percent}
								class:hover:border-primary-200={selectedTip !== percent}
								class:hover:text-primary-700={selectedTip !== percent}
								class:bg-primary-500={selectedTip === percent}
								class:border-primary-600={selectedTip === percent}
								class:text-text-inverted={selectedTip === percent}
								class:shadow-sm={selectedTip === percent}
								class:ring-2={selectedTip === percent}
								class:ring-primary-100={selectedTip === percent}
								class:ring-offset-1={selectedTip === percent}
								onclick={() => handleQuickTip(percent)}
							>
								{percent}%
							</button>
						{/each}
						<button type="button" class="h-10 rounded-xl {selectedTip === 'custom' ? 'bg-primary-500 border-primary-600 text-text-inverted shadow-sm' : 'bg-surface-50 border border-surface-200 text-text-secondary hover:bg-primary-50 hover:border-primary-200 hover:text-primary-700'} text-caption font-bold transition-all duration-200 hover:scale-105 active:scale-95" onclick={() => selectedTip = 'custom'}>
							Custom
						</button>
					</div>
					{#if selectedTip === 'custom'}
						<div class="mt-3 flex items-center gap-2">
							<span class="text-caption font-medium text-text-secondary">Tip amount:</span>
							<input
								type="number"
								bind:value={tip}
								min="0"
								step="1000"
								class="w-28 h-9 text-sm font-bold text-text-primary bg-surface-50 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 rounded-xl px-3 focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500"
							/>
						</div>
					{/if}
				</div>
			</div>

			<!-- Total Footer -->
			<div class="bg-surface-50 px-5 py-4 border-t border-surface-200">
				<div class="flex items-end justify-between">
					<div class="text-label font-bold text-text-tertiary">Estimated Total</div>
					<div class="text-section font-black text-text-primary tracking-tight tabular-nums">{formatCurrency(estimatedTotal)}</div>
				</div>
			</div>
		</section>

		<!-- Smart Rounding Options -->
		<section class="rounded-2xl bg-surface-0 shadow-card border border-surface-200 p-5 animate-slide-up animate-delay-100">
			<div class="flex items-center justify-between mb-3">
				<h2 class="text-label font-bold text-text-primary">Smart Rounding</h2>
				<span class="text-caption font-bold text-primary-600 bg-primary-100 px-2 py-0.5 rounded-lg">ACTIVE</span>
			</div>
			<div class="grid grid-cols-3 gap-1 p-1 bg-surface-100 rounded-2xl mb-3">
				<button
					type="button"
					class="py-2.5 rounded-xl text-caption font-bold text-text-secondary hover:bg-surface-0 hover:shadow-sm transition-all {roundingMode === 'down' ? 'bg-surface-0 shadow-sm border border-surface-200' : ''}"
					onclick={() => roundingMode = 'down'}
				>
					Down
				</button>
				<button
					type="button"
					class="py-2.5 rounded-xl text-caption font-bold text-text-secondary hover:bg-surface-0 hover:shadow-sm transition-all {roundingMode === 'exact' ? 'bg-surface-0 shadow-sm text-text-primary border border-surface-200' : ''}"
					onclick={() => roundingMode = 'exact'}
				>
					Exact
				</button>
				<button
					type="button"
					class="py-2.5 rounded-xl text-caption font-bold text-text-secondary hover:bg-surface-0 hover:shadow-sm transition-all {roundingMode === 'up' ? 'bg-surface-0 shadow-sm border border-surface-200' : ''}"
					onclick={() => roundingMode = 'up'}
				>
					Up
				</button>
			</div>
			<div class="flex items-start gap-2.5 rounded-xl bg-surface-50 border border-surface-100 p-3">
				<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-500 mt-0.5 shrink-0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
				<p class="text-caption text-text-secondary font-medium leading-relaxed">
					{#if roundingMode === 'exact'}
						Total will be exactly <span class="font-bold text-text-primary">{formatCurrency(estimatedTotal)}</span>. No rounding applied.
					{:else if roundingMode === 'up'}
						Each share rounded <span class="font-bold text-text-primary">up</span> to nearest IDR 1,000.
					{:else}
						Each share rounded <span class="font-bold text-text-primary">down</span> to nearest IDR 1,000.
					{/if}
				</p>
			</div>
		</section>

		<!-- Split Style Tabs -->
		<section class="rounded-2xl bg-surface-0 dark:bg-surface-800 shadow-card border border-surface-200 dark:border-surface-700 overflow-hidden animate-slide-up animate-delay-200">
			<div class="px-5 py-3 border-b border-surface-100 dark:border-surface-700">
				<h2 class="text-sm font-bold text-text-primary">Split Method</h2>
			</div>
			<div class="p-5">
				<div class="grid grid-cols-3 gap-3 mb-4">
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl transition-all duration-200 active:scale-[0.98] {splitMethod === 'equal' ? 'bg-primary-50 dark:bg-primary-900/30 border-2 border-primary-500 text-primary-700 dark:text-primary-300 shadow-sm' : 'bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-secondary dark:text-text-secondary hover:border-surface-300 dark:hover:border-surface-500 hover:shadow-sm hover:-translate-y-0.5'}"
						onclick={() => splitMethod = 'equal'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M8 3H3v5"/><path d="M12 22v-8"/><path d="M12 15V9"/><path d="M12 9H4"/><path d="M12 9h8"/><path d="M16 21h5v-5"/><path d="M8 21H3v-5"/></svg>
						<span class="text-xs font-extrabold">Equal</span>
					</button>
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl transition-all duration-200 active:scale-[0.98] {splitMethod === 'percentage' ? 'bg-primary-50 dark:bg-primary-900/30 border-2 border-primary-500 text-primary-700 dark:text-primary-300 shadow-sm' : 'bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-secondary dark:text-text-secondary hover:border-surface-300 dark:hover:border-surface-500 hover:shadow-sm hover:-translate-y-0.5'}"
						onclick={() => splitMethod = 'percentage'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>
						<span class="text-xs font-extrabold">% Split</span>
					</button>
					<button
						type="button"
						class="flex flex-col items-center justify-center gap-2 h-20 rounded-2xl transition-all duration-200 active:scale-[0.98] {splitMethod === 'item' ? 'bg-primary-50 dark:bg-primary-900/30 border-2 border-primary-500 text-primary-700 dark:text-primary-300 shadow-sm' : 'bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-secondary dark:text-text-secondary hover:border-surface-300 dark:hover:border-surface-500 hover:shadow-sm hover:-translate-y-0.5'}"
						onclick={() => splitMethod = 'item'}
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
						<span class="text-xs font-extrabold">By Item</span>
					</button>
				</div>

				{#if splitMethod === 'equal'}
					<div class="flex items-start gap-3">
						<div class="h-10 w-10 shrink-0 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
						</div>
						<div>
							<p class="text-sm font-bold text-text-primary">Equal Split</p>
							<p class="text-xs text-text-secondary leading-relaxed mt-0.5">We'll divide the total bill evenly between everyone added below.</p>
						</div>
					</div>
				{:else if splitMethod === 'percentage'}
					<div class="space-y-3">
						<div class="flex items-center justify-between">
							<p class="text-sm font-bold text-text-primary">Custom Percentages</p>
							<span class="text-caption font-bold {percentageTotal === 100 ? 'text-success' : 'text-error'}">{percentageTotal}%</span>
						</div>
						{#each people as person, index}
							<div class="flex items-center gap-3">
								<span class="text-sm font-medium text-text-secondary w-16 truncate">{person.name}</span>
								<input
									type="range"
									min="0"
									max="100"
									bind:value={percentages[index]}
									class="flex-1 h-2 accent-primary-500"
								/>
								<div class="flex items-center gap-1 w-16">
									<input
										type="number"
										min="0"
										max="100"
										bind:value={percentages[index]}
										class="w-12 h-8 rounded-lg border border-surface-200 bg-surface-50 text-center text-sm font-bold text-text-primary focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
									/>
									<span class="text-xs text-text-tertiary font-bold">%</span>
								</div>
							</div>
						{/each}
						{#if percentageTotal !== 100}
							<p class="text-caption text-error font-medium">Percentages must add up to 100%</p>
						{/if}
					</div>
				{:else if splitMethod === 'item'}
					{#if receiptItems.length === 0}
						<div class="flex items-start gap-3">
							<div class="h-10 w-10 shrink-0 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center">
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
							</div>
							<div>
								<p class="text-sm font-bold text-text-primary">No items to assign</p>
								<p class="text-xs text-text-secondary leading-relaxed mt-0.5">Scan a receipt first to populate items, then assign them to people here.</p>
							</div>
						</div>
					{:else}
						<div class="space-y-3">
							<p class="text-sm font-bold text-text-primary">Assign items to people</p>
							{#each receiptItems as item, itemIndex}
								<div class="bg-surface-50 dark:bg-surface-700/50 rounded-xl p-3 border border-surface-200 dark:border-surface-600">
									<div class="flex justify-between items-center mb-2">
										<span class="text-sm font-medium text-text-primary">{item.name}</span>
										<span class="text-sm font-bold text-text-primary tabular-nums">Rp {item.price.toLocaleString('id-ID')}</span>
									</div>
									<div class="flex flex-wrap gap-1.5">
										{#each people as person, personIndex}
											<button
												type="button"
												class="px-2.5 py-1 rounded-lg text-xs font-semibold transition-all active:scale-95 {item.assignedTo.includes(personIndex) ? 'bg-primary-500 text-white shadow-sm' : 'bg-surface-100 dark:bg-surface-600 text-text-secondary hover:bg-primary-50 hover:text-primary-600'}"
												onclick={() => toggleItemAssignment(itemIndex, personIndex)}
											>
												{person.name}
											</button>
										{/each}
									</div>
								</div>
							{/each}
						</div>
					{/if}
				{/if}
			</div>
		</section>

		<!-- People Manager -->
		<section class="rounded-2xl bg-surface-0 dark:bg-surface-800 shadow-card border border-surface-200 dark:border-surface-700 overflow-hidden animate-slide-up animate-delay-300">
			<div class="px-5 py-3 border-b border-surface-100 dark:border-surface-700 flex justify-between items-center">
				<h2 class="text-sm font-bold text-text-primary">People</h2>
				<span class="bg-surface-100 dark:bg-surface-700 text-text-secondary dark:text-text-secondary px-2.5 py-0.5 rounded-lg text-xs font-bold">{people.length}</span>
			</div>
			<div class="p-5 space-y-4">
				{#each people as person, index}
					<div class="bg-surface-50 dark:bg-surface-700/50 rounded-2xl p-3 border border-surface-200 dark:border-surface-600 animate-scale-in transition-all duration-200" style="animation-delay: {Math.min(index * 50, 150)}ms;">
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
									class="bg-transparent border-none p-0 text-sm font-bold text-text-primary focus:ring-0 w-full {errors[`person-${index}`] ? 'text-red-600' : ''}"
								/>
								{#if errors[`person-${index}`]}
									<p class="text-xs text-red-600 dark:text-red-400">{errors[`person-${index}`]}</p>
								{:else}
									<div class="text-xs text-text-secondary">{splitMethod === 'percentage' ? `${percentages[index]}%` : `${(100 / people.length).toFixed(1)}%`} share</div>
								{/if}
							</div>
							<button
								type="button"
								class="h-11 w-11 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg text-text-tertiary hover:bg-rose-50 dark:hover:bg-rose-900/30 hover:text-rose-500 dark:hover:text-rose-400 transition-colors"
								aria-label="Remove {person.name}"
								onclick={() => removePerson(index)}
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
							</button>
						</div>

						<div class="flex items-center gap-2">
							<button
								type="button"
								class="flex-1 h-10 rounded-xl bg-surface-0 dark:bg-surface-600 border border-surface-200 dark:border-surface-500 shadow-sm text-xs font-bold text-text-primary dark:text-text-primary flex items-center justify-center gap-2 hover:bg-surface-50 dark:hover:bg-surface-500 active:scale-95 transition-all"
								onclick={() => splitMethod = 'item'}
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="M12 5v14M5 12h14"/></svg>
								Assign Items
							</button>
							<div class="px-3 h-10 rounded-xl bg-surface-0 dark:bg-surface-600 border border-surface-200 dark:border-surface-500 flex items-center justify-center text-sm font-black text-text-primary dark:text-text-inverted shadow-sm min-w-[90px] tabular-nums">
								{formatCurrency(shares[index].total)}
							</div>
						</div>
					</div>
				{/each}

				<!-- Add Button -->
				<button
					type="button"
					class="w-full h-12 rounded-2xl border-2 border-dashed border-surface-300 dark:border-surface-600 text-text-secondary font-bold text-sm flex items-center justify-center gap-2 hover:border-primary-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all active:scale-[0.99]"
					onclick={addPerson}
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
					Add Person
				</button>
			</div>
		</section>

		<!-- Action Area -->
		<section class="pt-2 animate-slide-up animate-delay-400">
			<button
				type="button"
				class="w-full h-14 rounded-2xl bg-primary-500 dark:bg-primary-600 text-white font-extrabold text-lg shadow-lg shadow-primary-500/30 dark:shadow-primary-900/50 flex items-center justify-center gap-2 active:scale-[0.98] transition-all duration-200 hover:bg-primary-600 hover:shadow-xl hover:shadow-primary-500/40 group"
				onclick={handleCalculateSplit}
			>
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
				Calculate Split
			</button>

			<button
				type="button"
				class="mt-3 w-full h-14 rounded-2xl bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 text-text-primary dark:text-text-primary font-bold text-sm shadow-sm flex items-center justify-center gap-2 active:scale-[0.98] transition-all duration-200 hover:bg-surface-50 dark:hover:bg-surface-600 hover:shadow-md"
				onclick={handleSaveTemplate}
			>
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
				Save as Template
			</button>
		</section>
	</main>
</div>
