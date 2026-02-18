<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { receiptStore, currencyStore } from '$lib/stores';

	let items = $state([
		{ id: 1, name: 'Double Cheeseburger', price: 14.50 },
		{ id: 2, name: 'Sweet Potato Fries', price: 6.00 },
		{ id: 3, name: 'Vanilla Shake', price: 5.50 },
	]);

	let taxDetected = $state(10);
	let taxEnabled = $state(true);
	let subtotal = $derived(items.reduce((sum, item) => sum + item.price, 0));
	let taxAmount = $derived(subtotal * (taxDetected / 100));
	let totalAmount = $derived(subtotal + taxAmount);

	onMount(() => {
		currencyStore.init().catch(() => {});
	});

	function handleFileUpload() {
		// Implementation for file upload
	}

	function handleOpenCamera() {
		// Implementation for camera
	}

	function handleAddItem() {
		items = [...items, { id: Date.now(), name: '', price: 0 }];
	}

	function handleItemNameChange(id: number, name: string) {
		items = items.map(item =>
			item.id === id ? { ...item, name } : item
		);
	}

	function handleItemPriceChange(id: number, price: string) {
		const parsedPrice = parseFloat(price) || 0;
		// Ensure price is not negative
		if (parsedPrice < 0) {
			return;
		}
		items = items.map(item =>
			item.id === id ? { ...item, price: parsedPrice } : item
		);
	}

	function handleRemoveItem(id: number) {
		items = items.filter(item => item.id !== id);
	}

	function handleShare() {
		// Implementation for sharing
	}

	function handleConfirm() {
		// Validate that we have items
		if (items.length === 0 || items.every(item => !item.name || !item.price)) {
			alert('Please add at least one item with name and price');
			return;
		}

		// Save receipt data and proceed to split creation
		const receiptData = {
			items: items,
			tax: taxEnabled ? taxAmount : 0,
			taxRate: taxDetected,
			total: totalAmount
		};

		// Store in receipt store for the split page to use
		receiptStore.setReceipt(receiptData);

		// Navigate to split creation with the receipt data
		goto('/split');
	}
</script>

<svelte:head>
	<title>Scan Receipt - Split Bill</title>
	<meta name="color-scheme" content="light" />
</svelte:head>

<div class="w-full min-h-dvh flex flex-col bg-slate-50 text-slate-900 font-sans">
	<!-- Header (safe area) - EXACT: pt-14 px-4, h-11 w-11 rounded-xl bg-white shadow-md shadow-slate-200 -->
	<header class="shrink-0 pt-14 px-4">
		<div class="flex items-center justify-between">
			<a href="/" class="h-11 w-11 inline-flex items-center justify-center rounded-xl bg-white shadow-md shadow-slate-200">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700"><path d="m15 18-6-6 6"/><path d="m18 15-6-6"/></svg>
			</a>

			<div class="text-center">
				<p class="text-base font-semibold">Scan Receipt</p>
			</div>

			<a href="#help" class="h-11 w-11 inline-flex items-center justify-center rounded-xl bg-white shadow-md shadow-slate-200">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 12h.01"/></svg>
			</a>
		</div>
	</header>

	<!-- Main -->
	<main class="flex-1 overflow-y-auto px-4 pt-5 pb-6">
		<!-- Upload zone - EXACT: rounded-3xl border-2 border-dashed border-primary-400 bg-primary-50 -->
		<section class="mt-5">
			<button type="button" class="w-full rounded-3xl border-2 border-dashed border-primary-400 bg-primary-50">
				<div class="px-5 py-10">
					<div class="mx-auto flex flex-col items-center">
						<!-- Camera icon - EXACT: h-20 w-20 rounded-3xl bg-white ring-1 ring-primary-200, width="32" height="32" -->
						<div class="h-20 w-20 rounded-3xl bg-white ring-1 ring-primary-200 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-600"><path d="m23 19-7-16 2v-8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8"/><path d="M16 3h5"/><path d="M21 14V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9"/><path d="M21 14v7"/></svg>
						</div>

						<p class="mt-4 text-base font-semibold">Tap to scan</p>
						<p class="mt-1 text-sm text-slate-600 text-center">Or upload a photo/PDF of your receipt</p>
					</div>
				</div>
			</button>
		</section>

		<!-- Confidence section - EXACT: px-4 py-3 bg-slate-50, h-5 w-5 rounded-full bg-green-500 -->
		<section class="mt-5 rounded-3xl bg-white shadow-md shadow-slate-200 ring-1 ring-slate-200">
			<div class="px-4 py-3 bg-slate-50 flex items-center justify-between">
				<div class="flex items-center gap-2">
					<div class="h-5 w-5 rounded-full bg-green-500 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white"><path d="M20 6 9 17 4 18"/><path d="m4 18 9-17"/></svg>
					</div>
					<span class="text-xs font-bold text-slate-700 uppercase tracking-wider">Scan Complete</span>
				</div>
				<div class="flex items-center gap-1.5 rounded-full bg-green-50 px-2 py-1 ring-1 ring-green-200">
					<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-green-600"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
					<span class="text-xs font-bold text-green-700">98% Confidence</span>
				</div>
			</div>

			<div class="p-4">
				<!-- Items - EXACT: h-6 w-6 rounded-full remove button, border-none bg-transparent inputs -->
				<div class="space-y-3">
					{#each items as item}
						<div class="flex items-center gap-3">
							<button
								type="button"
								class="h-6 w-6 rounded-full bg-slate-100 flex items-center justify-center hover:bg-rose-50 hover:text-rose-500 transition-colors"
								onclick={() => handleRemoveItem(item.id)}
								aria-label="Remove item"
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-600"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
							</button>
							<input
								type="text"
								value={item.name}
								oninput={(e) => handleItemNameChange(item.id, e.currentTarget.value)}
								class="flex-1 border-none bg-transparent p-0 text-sm font-semibold text-slate-900 focus:ring-0 focus:outline-none"
								placeholder="Item name"
							/>
							<div class="flex items-center gap-1">
								<span class="text-xs text-slate-400">$</span>
								<input
									type="number"
									value={item.price}
									oninput={(e) => handleItemPriceChange(item.id, e.currentTarget.value)}
									class="w-16 border-none bg-transparent p-0 text-right text-sm font-bold text-slate-900 focus:ring-0 focus:outline-none tabular-nums {item.price < 0 ? 'text-red-600' : ''}"
									placeholder="0.00"
									step="0.01"
									min="0"
								/>
							</div>
						</div>
					{/each}

					<div class="pt-1 flex items-center justify-between">
						<button
							type="button"
							onclick={handleAddItem}
							class="flex items-center gap-1.5 text-xs font-bold text-primary-600"
						>
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/></svg>
							Add Item
						</button>
						<span class="text-xs font-medium text-slate-400">Subtotal: ${subtotal.toFixed(2)}</span>
					</div>
				</div>

				<!-- Tax section - EXACT: h-7 w-7 rounded-lg bg-orange-50, toggle h-6 w-10 bg-primary-500 -->
				<div class="mt-4 pt-4 border-t border-slate-100 space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<div class="h-7 w-7 rounded-lg bg-orange-50 flex items-center justify-center text-orange-500">
								<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 1 0 7h5a3.5 3.5 0 0 1 0 7H17"/></svg>
							</div>
							<div class="leading-none">
								<p class="text-xs font-bold text-slate-700">Tax Detected: {taxDetected}%</p>
								<button class="text-xs font-medium text-primary-600 underline decoration-primary-200 underline-offset-2 mt-0.5">Edit Rate</button>
							</div>
						</div>
						<button type="button" class="relative h-6 w-10 rounded-full bg-primary-500">
							<span class="absolute right-1 top-1 h-4 w-4 rounded-full bg-white"></span>
						</button>
					</div>

					<!-- Total Card -->
					<div class="flex items-center justify-between rounded-xl bg-slate-50 p-3 ring-1 ring-slate-100">
						<span class="text-sm font-semibold text-slate-600">Total Amount</span>
						<div class="flex items-baseline gap-1">
							<span class="text-xs font-bold text-slate-400">USD</span>
							<span class="text-xl font-bold text-slate-900 tabular-nums">${totalAmount.toFixed(2)}</span>
						</div>
					</div>
				</div>

				<!-- Actions -->
				<div class="mt-5 grid grid-cols-2 gap-3">
					<button
						type="button"
						onclick={handleShare}
						class="flex h-10 items-center justify-center gap-2 rounded-xl bg-white text-xs font-bold text-slate-700 shadow-sm ring-1 ring-slate-200"
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-500"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
						Share
					</button>
					<button
						type="button"
						onclick={handleConfirm}
						class="flex h-10 items-center justify-center gap-2 rounded-xl bg-primary-500 text-xs font-bold text-white shadow-md shadow-primary-200"
					>
						<span>Confirm</span>
						<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
					</button>
				</div>
			</div>
		</section>

		<!-- Help section - EXACT: rounded-3xl bg-primary-50 ring-1 ring-primary-200 -->
		<section class="mt-5 rounded-3xl bg-primary-50 ring-1 ring-primary-200">
			<div class="p-4">
				<div class="flex items-start gap-3">
					<div class="h-11 w-11 rounded-2xl bg-white ring-1 ring-primary-200 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-600"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
					</div>
					<div class="flex-1">
						<p class="text-sm font-semibold">Tips for best results</p>
						<ul class="mt-2 space-y-2 text-sm text-slate-700">
							<li class="flex gap-2">
								<span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary-500 shrink-0"></span>
								<span>Place receipt on a flat surface with good lighting.</span>
							</li>
							<li class="flex gap-2">
								<span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary-500 shrink-0"></span>
								<span>Make sure the total and tax are visible in the photo.</span>
							</li>
							<li class="flex gap-2">
								<span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary-500 shrink-0"></span>
								<span>Keep the camera steady—no blur.</span>
							</li>
						</ul>
						<div class="mt-4 flex gap-3">
							<a href="#learn-more" class="h-11 px-4 inline-flex items-center justify-center rounded-2xl bg-white ring-1 ring-primary-200 text-sm font-semibold text-primary-700 shadow-md shadow-primary-100">
								Learn more
							</a>
							<a href="#troubleshoot" class="h-11 px-4 inline-flex items-center justify-center rounded-2xl bg-primary-500 text-sm font-semibold text-white shadow-md shadow-primary-200">
								Troubleshoot
							</a>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Extra spacing -->
		<div class="h-24"></div>
	</main>

	<!-- Bottom nav - EXACT: grid grid-cols-4 gap-2, h-14 with active state bg-primary-50 -->
	<footer class="shrink-0 pb-[34px]">
		<nav class="w-full bg-white border-t border-slate-200">
			<div class="px-3 pt-2">
				<div class="grid grid-cols-4 gap-2">
					<a href="/" class="h-14 rounded-2xl inline-flex flex-col items-center justify-center gap-1 text-slate-600">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 7"/><path d="M9 21V9"/></svg>
						<span class="text-xs font-semibold">Home</span>
					</a>

					<a href="/history" class="h-14 rounded-2xl inline-flex flex-col items-center justify-center gap-1 text-slate-600">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 1 9 9 9 9 0 0 1-9-9 9 9 0 0 1-6-2.3L3 8"/><path d="m3 3 9 9"/><path d="m12 15V3"/></svg>
						<span class="text-xs font-semibold">History</span>
					</a>

					<!-- Active: Scan -->
					<a href="/receipt" class="h-14 rounded-2xl inline-flex flex-col items-center justify-center gap-1 bg-primary-50 text-primary-700 ring-1 ring-primary-200">
						<span class="h-9 w-9 rounded-2xl bg-primary-500 shadow-md shadow-primary-200 inline-flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
						</span>
						<span class="text-xs font-extrabold">Scan</span>
					</a>

					<a href="/settings" class="h-14 rounded-2xl inline-flex flex-col items-center justify-center gap-1 text-slate-600">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0-.73 2.73l.08.15a2 2 0 0 1 0 2l-.08.15a2 2 0 0 0 .73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 0 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.08-.14a2 2 0 0 1 0-2l.08-.15a2 2 0 0 0-.73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
						<span class="text-xs font-semibold">Settings</span>
					</a>
				</div>
			</div>
		</nav>
	</footer>
</div>
