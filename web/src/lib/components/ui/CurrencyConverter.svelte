<script lang="ts">
	import { fly } from 'svelte/transition';

	interface Props {
		amount?: number;
		fromCurrency?: string;
		onClose: () => void;
	}

	let { amount = 100000, fromCurrency = 'IDR', onClose }: Props = $props();

	const currencies = [
		{ code: 'IDR', name: 'Indonesian Rupiah', symbol: 'Rp', flag: '🇮🇩', rate: 1 },
		{ code: 'USD', name: 'US Dollar', symbol: '$', flag: '🇺🇸', rate: 0.000064 },
		{ code: 'EUR', name: 'Euro', symbol: '€', flag: '🇪🇺', rate: 0.000059 },
		{ code: 'JPY', name: 'Japanese Yen', symbol: '¥', flag: '🇯🇵', rate: 0.0096 },
		{ code: 'SGD', name: 'Singapore Dollar', symbol: 'S$', flag: '🇸🇬', rate: 0.000086 },
		{ code: 'MYR', name: 'Malaysian Ringgit', symbol: 'RM', flag: '🇲🇾', rate: 0.00030 },
		{ code: 'AUD', name: 'Australian Dollar', symbol: 'A$', flag: '🇦🇺', rate: 0.00010 },
		{ code: 'GBP', name: 'British Pound', symbol: '£', flag: '🇬🇧', rate: 0.000051 },
	];

	let sourceAmount = $state(amount);
	let sourceCurrency = $state(fromCurrency);
	let targetCurrency = $state('USD');
	let showSourceDropdown = $state(false);
	let showTargetDropdown = $state(false);

	function getCurrency(code: string) {
		return currencies.find(c => c.code === code) || currencies[0];
	}

	function convert(amount: number, from: string, to: string): number {
		const fromRate = getCurrency(from).rate;
		const toRate = getCurrency(to).rate;
		return (amount / fromRate) * toRate;
	}

	const convertedAmount = $derived(convert(sourceAmount, sourceCurrency, targetCurrency));

	function formatNumber(num: number, currency: string): string {
		const curr = getCurrency(currency);
		return new Intl.NumberFormat('en-US', {
			minimumFractionDigits: num >= 100 ? 0 : 2,
			maximumFractionDigits: 2
		}).format(num);
	}

	function swapCurrencies() {
		const temp = sourceCurrency;
		sourceCurrency = targetCurrency;
		targetCurrency = temp;
	}
</script>

<svelte:head>
	<title>Currency Converter - Split Bill</title>
</svelte:head>

<!-- Backdrop -->
<div 
	class="fixed inset-0 bg-black/50 z-50 flex items-end justify-center"
	onclick={onClose}
	onkeydown={(e) => e.key === 'Escape' && onClose()}
	role="dialog"
	aria-modal="true"
	aria-label="Currency Converter"
>
	<!-- Modal -->
	<div
		class="w-full max-w-lg bg-white rounded-t-3xl shadow-2xl overflow-hidden"
		transition:fly={{ y: 100, duration: 300 }}
		onclick={(e) => e.stopPropagation()}
		style="padding-bottom: env(safe-area-inset-bottom, 0);"
	>
		<!-- Handle -->
		<div class="flex justify-center pt-3 pb-2">
			<div class="h-1.5 w-12 rounded-full bg-slate-300"></div>
		</div>

		<!-- Header -->
		<div class="px-5 pb-3 flex items-center justify-between">
			<h2 class="text-lg font-bold text-slate-900">Currency Converter</h2>
			<button 
				type="button"
				onclick={onClose}
				class="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-slate-200 transition-colors"
			>
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
			</button>
		</div>

		<!-- Content -->
		<div class="px-5 pb-6 space-y-4">
			<!-- Source Currency -->
			<div class="rounded-2xl bg-slate-50 border border-slate-200 p-4">
				<div class="flex items-center justify-between mb-3">
					<span class="text-xs font-bold text-slate-500 uppercase tracking-wider">From</span>
					<button 
						type="button"
						onclick={() => showSourceDropdown = !showSourceDropdown}
						class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-slate-200 shadow-sm active:scale-95 transition-transform"
					>
						<span class="text-lg">{getCurrency(sourceCurrency).flag}</span>
						<span class="text-sm font-bold text-slate-900">{getCurrency(sourceCurrency).code}</span>
						<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m6 9 6 6 6-6"/></svg>
					</button>
				</div>
				<div class="flex items-center gap-2">
					<span class="text-2xl font-bold text-slate-400">{getCurrency(sourceCurrency).symbol}</span>
					<input
						type="number"
						bind:value={sourceAmount}
						class="flex-1 bg-transparent text-3xl font-black text-slate-900 focus:outline-none tabular-nums"
						min="0"
					/>
				</div>
			</div>

			<!-- Swap Button -->
			<div class="flex justify-center -my-2 relative z-10">
				<button 
					type="button"
					onclick={swapCurrencies}
					class="h-12 w-12 rounded-full bg-indigo-500 text-white shadow-lg shadow-indigo-500/30 flex items-center justify-center active:scale-90 transition-transform"
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 16V4m0 0L3 8m4-4l4 4"/><path d="M17 8v12m0 0l4-4m-4 4l-4-4"/></svg>
				</button>
			</div>

			<!-- Target Currency -->
			<div class="rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 p-4 text-white shadow-lg">
				<div class="flex items-center justify-between mb-3">
					<span class="text-xs font-bold text-indigo-200 uppercase tracking-wider">To</span>
					<button 
						type="button"
						onclick={() => showTargetDropdown = !showTargetDropdown}
						class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/20 backdrop-blur-sm border border-white/30 active:scale-95 transition-transform"
					>
						<span class="text-lg">{getCurrency(targetCurrency).flag}</span>
						<span class="text-sm font-bold">{getCurrency(targetCurrency).code}</span>
						<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white/70"><path d="m6 9 6 6 6-6"/></svg>
					</button>
				</div>
				<div class="flex items-center gap-2">
					<span class="text-2xl font-bold text-indigo-200">{getCurrency(targetCurrency).symbol}</span>
					<span class="flex-1 text-3xl font-black tabular-nums">{formatNumber(convertedAmount, targetCurrency)}</span>
				</div>
			</div>

			<!-- Exchange Rate Info -->
			<div class="flex items-center justify-center gap-2 py-2">
				<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
				<span class="text-xs text-slate-500">
					1 {sourceCurrency} = {formatNumber(convert(1, sourceCurrency, targetCurrency), targetCurrency)} {targetCurrency}
				</span>
			</div>

			<!-- Currency List -->
			{#if showSourceDropdown}
				<div class="rounded-2xl bg-white border border-slate-200 shadow-xl max-h-48 overflow-y-auto">
					{#each currencies as curr}
						<button
							type="button"
							onclick={() => { sourceCurrency = curr.code; showSourceDropdown = false; }}
							class="w-full px-4 py-3 flex items-center gap-3 hover:bg-slate-50 transition-colors {curr.code === sourceCurrency ? 'bg-indigo-50' : ''}"
						>
							<span class="text-xl">{curr.flag}</span>
							<span class="flex-1 text-left">
								<span class="text-sm font-bold text-slate-900">{curr.code}</span>
								<span class="text-xs text-slate-500 ml-2">{curr.name}</span>
							</span>
							<span class="text-sm font-medium text-slate-600">{curr.symbol}</span>
						</button>
					{/each}
				</div>
			{/if}

			{#if showTargetDropdown}
				<div class="rounded-2xl bg-white border border-slate-200 shadow-xl max-h-48 overflow-y-auto">
					{#each currencies as curr}
						<button
							type="button"
							onclick={() => { targetCurrency = curr.code; showTargetDropdown = false; }}
							class="w-full px-4 py-3 flex items-center gap-3 hover:bg-slate-50 transition-colors {curr.code === targetCurrency ? 'bg-indigo-50' : ''}"
						>
							<span class="text-xl">{curr.flag}</span>
							<span class="flex-1 text-left">
								<span class="text-sm font-bold text-slate-900">{curr.code}</span>
								<span class="text-xs text-slate-500 ml-2">{curr.name}</span>
							</span>
							<span class="text-sm font-medium text-slate-600">{curr.symbol}</span>
						</button>
					{/each}
				</div>
			{/if}

			<!-- Quick Amounts -->
			<div class="grid grid-cols-4 gap-2">
				{#each [10000, 50000, 100000, 500000] as quickAmount}
					<button
						type="button"
						onclick={() => sourceAmount = quickAmount}
						class="h-10 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold hover:bg-slate-200 active:scale-95 transition-all {sourceAmount === quickAmount ? 'ring-2 ring-indigo-500 bg-indigo-50 text-indigo-700' : ''}"
					>
						{quickAmount >= 1000000 ? `${quickAmount / 1000000}M` : `${quickAmount / 1000}k`}
					</button>
				{/each}
			</div>

			<!-- Disclaimer -->
			<p class="text-[10px] text-slate-400 text-center">
				Rates are approximate. Last updated: Today, 12:00 PM WIB
			</p>
		</div>
	</div>
</div>
