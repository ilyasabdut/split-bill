<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { receiptStore, currencyStore } from '$lib/stores';
	import ErrorMessage from '$lib/components/ui/ErrorMessage.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';

	interface ReceiptItem {
		id: number;
		name: string;
		price: number;
	}

	interface ValidationError {
		itemId?: number;
		message: string;
	}

	let items = $state<ReceiptItem[]>([
		{ id: 1, name: 'Double Cheeseburger', price: 14.50 },
		{ id: 2, name: 'Sweet Potato Fries', price: 6.00 },
		{ id: 3, name: 'Vanilla Shake', price: 5.50 },
	]);

	let taxDetected = $state(10);
	let taxEnabled = $state(true);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let validationErrors = $state<ValidationError[]>([]);
	let scanStatus = $state<'idle' | 'scanning' | 'success' | 'error'>('idle');

	let subtotal = $derived(items.reduce((sum, item) => sum + item.price, 0));
	let taxAmount = $derived(subtotal * (taxDetected / 100));
	let totalAmount = $derived(subtotal + taxAmount);

	onMount(() => {
		currencyStore.init().catch(() => {
			setError('Failed to load currency settings');
		});
	});

	function setError(message: string | null) {
		error = message;
		if (message) {
			scanStatus = 'error';
		}
	}

	function clearError() {
		error = null;
	}

	function validateItemName(name: string): { valid: boolean; error?: string } {
		if (!name.trim()) {
			return { valid: false, error: 'Item name is required' };
		}
		if (name.length > 100) {
			return { valid: false, error: 'Name must be 100 characters or less' };
		}
		return { valid: true };
	}

	function validateItemPrice(price: number): { valid: boolean; error?: string } {
		if (isNaN(price)) {
			return { valid: false, error: 'Price must be a number' };
		}
		if (price < 0) {
			return { valid: false, error: 'Price cannot be negative' };
		}
		if (price > 999999.99) {
			return { valid: false, error: 'Price exceeds maximum allowed' };
		}
		return { valid: true };
	}

	async function handleFileUpload(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];

		if (!file) return;

		// Validate file type
		const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
		if (!allowedTypes.includes(file.type)) {
			setError('Please upload an image (JPG, PNG, WebP) or PDF file');
			return;
		}

		// Validate file size (10MB max)
		const maxSize = 10 * 1024 * 1024;
		if (file.size > maxSize) {
			setError('File size must be less than 10MB');
			return;
		}

		loading = true;
		scanStatus = 'scanning';
		clearError();

		try {
			// Simulate OCR processing
			await new Promise(resolve => setTimeout(resolve, 2000));

			// Demo: Add scanned items
			items = [
				...items,
				{ id: Date.now(), name: 'Scanned Item', price: 15.00 }
			];

			scanStatus = 'success';
		} catch (err) {
			setError('Failed to scan receipt. Please try again or enter items manually.');
			scanStatus = 'error';
		} finally {
			loading = false;
			input.value = ''; // Reset input
		}
	}

	async function handleOpenCamera() {
		loading = true;
		clearError();

		try {
			// Check if camera is available
			const stream = await navigator.mediaDevices.getUserMedia({
				video: { facingMode: 'environment' }
			});

			// Stop stream immediately (demo)
			stream.getTracks().forEach(track => track.stop());

			scanStatus = 'scanning';

			// Simulate camera scan
			await new Promise(resolve => setTimeout(resolve, 2000));

			// Demo: Add scanned item
			items = [...items, { id: Date.now(), name: 'Camera Scan Item', price: 12.50 }];

			scanStatus = 'success';
		} catch (err) {
			if (err instanceof Error && err.name === 'NotAllowedError') {
				setError('Camera access denied. Please enable camera permissions or upload an image.');
			} else if (err instanceof Error && err.name === 'NotFoundError') {
				setError('No camera found on this device. Please upload an image instead.');
			} else {
				setError('Failed to open camera. Please try again or upload an image.');
			}
			scanStatus = 'error';
		} finally {
			loading = false;
		}
	}

	function handleAddItem() {
		if (loading) return;

		const newItem: ReceiptItem = {
			id: Date.now(),
			name: '',
			price: 0
		};

		items = [...items, newItem];
	}

	function handleItemNameChange(id: number, name: string) {
		clearError();
		validationErrors = validationErrors.filter(e => e.itemId !== id);

		const validation = validateItemName(name);
		if (!validation.valid && validation.error) {
			validationErrors.push({ itemId: id, message: validation.error });
		}

		items = items.map(item =>
			item.id === id ? { ...item, name: name.trim() } : item
		);
	}

	function handleItemPriceChange(id: number, price: string) {
		clearError();
		validationErrors = validationErrors.filter(e => e.itemId !== id);

		const parsedPrice = parseFloat(price);

		const validation = validateItemPrice(parsedPrice);
		if (!validation.valid && validation.error) {
			validationErrors.push({ itemId: id, message: validation.error });
			return;
		}

		items = items.map(item =>
			item.id === id ? { ...item, price: isNaN(parsedPrice) ? 0 : parsedPrice } : item
		);
	}

	function handleRemoveItem(id: number) {
		if (items.length <= 1) {
			setError('At least one item is required');
			return;
		}

		items = items.filter(item => item.id !== id);
		validationErrors = validationErrors.filter(e => e.itemId !== id);
	}

	async function handleShare() {
		if (items.length === 0 || !items.some(item => item.name && item.price > 0)) {
			setError('Please add at least one valid item before sharing');
			return;
		}

		loading = true;
		clearError();

		try {
			// Check if Web Share API is available
			if (navigator.share) {
				const total = items.reduce((sum, item) => sum + item.price, 0);
				await navigator.share({
					title: 'Split Bill Receipt',
					text: `Total: $${total.toFixed(2)} - ${items.length} items`,
					url: window.location.href
				});
			} else {
				// Fallback: copy to clipboard
				const text = items.map(item => `${item.name}: $${item.price.toFixed(2)}`).join('\n');
				await navigator.clipboard.writeText(text);
				alert('Receipt copied to clipboard!');
			}
		} catch (err) {
			if (err instanceof Error && err.name !== 'AbortError') {
				setError('Failed to share. Please try again.');
			}
		} finally {
			loading = false;
		}
	}

	async function handleConfirm() {
		clearError();
		validationErrors = [];

		// Validate that we have items
		if (items.length === 0) {
			setError('Please add at least one item');
			return;
		}

		// Validate all items
		let hasValidItems = false;
		for (const item of items) {
			const nameValidation = validateItemName(item.name);
			const priceValidation = validateItemPrice(item.price);

			if (!nameValidation.valid) {
				validationErrors.push({ itemId: item.id, message: nameValidation.error! });
			}
			if (!priceValidation.valid) {
				validationErrors.push({ itemId: item.id, message: priceValidation.error! });
			}

			if (nameValidation.valid && priceValidation.valid) {
				hasValidItems = true;
			}
		}

		if (!hasValidItems) {
			setError('Please add at least one item with a valid name and price');
			return;
		}

		// Save receipt data and proceed to split creation
		const receiptData = {
			items: items.filter(item => item.name.trim() && item.price >= 0),
			tax: taxEnabled ? taxAmount : 0,
			taxRate: taxDetected,
			total: totalAmount
		};

		try {
			// Store in receipt store for the split page to use
			receiptStore.setReceipt(receiptData);

			// Navigate to split creation with the receipt data
			await goto('/split');
		} catch (err) {
			setError('Failed to proceed. Please try again.');
		}
	}
</script>

<svelte:head>
	<title>Scan Receipt - Split Bill</title>
	<meta name="color-scheme" content="light" />
</svelte:head>

<div class="w-full min-h-dvh flex flex-col bg-surface-50 text-text-primary font-sans">
	<header
		class="shrink-0 px-4"
		style="padding-top: max(env(safe-area-inset-top), 3.5rem);"
	>
		<div class="flex items-center justify-between max-w-lg mx-auto">
			<a href="/" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-xl bg-surface-0 dark:bg-surface-800 shadow-card border border-surface-200 hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors" aria-label="Go back home">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="m15 18-6-6 6"/><path d="m18 15-6-6"/></svg>
			</a>

			<div class="text-center">
				<p class="text-body font-semibold">Scan Receipt</p>
			</div>

			<a href="#help" class="h-11 w-11 min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-xl bg-surface-0 dark:bg-surface-800 shadow-card border border-surface-200 hover:bg-surface-50 dark:hover:bg-surface-700 transition-colors" aria-label="Get help">
				<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 12h.01"/></svg>
			</a>
		</div>
	</header>

	<main class="flex-1 overflow-y-auto px-4 pt-5 pb-6 max-w-lg mx-auto w-full" style="padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 2rem);">
		<!-- Error Message -->
		{#if error}
			<ErrorMessage
				title="Scan Error"
				message={error}
				onDismiss={clearError}
				variant="inline"
			/>
		{/if}

		<!-- Empty State -->
		{#if items.length === 0 && scanStatus === 'idle'}
			<EmptyState
				title="No items yet"
				description="Scan a receipt or add items manually to get started."
				action={{
					label: 'Add First Item',
					onclick: handleAddItem
				}}
			/>
		{/if}

		<section class="mt-section" aria-label="Receipt items">
			<div class="w-full rounded-2xl border-2 border-dashed border-primary-500 bg-primary-50 dark:bg-surface-800 transition-all duration-200">
				<div class="px-5 py-10">
					<div class="mx-auto flex flex-col items-center">
						{#if loading && scanStatus === 'scanning'}
							<div class="h-20 w-20 rounded-xl bg-surface-0 dark:bg-surface-700 ring-1 ring-primary-200 dark:ring-primary-800 flex items-center justify-center animate-scale-in">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="32"
									height="32"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
									class="text-primary-500 animate-spin"
								>
									<path d="M21 12a9 9 0 1 1-6.219-8.56" />
								</svg>
							</div>
							<p class="mt-4 text-body font-semibold animate-fade-in">Scanning receipt...</p>
							<p class="mt-1 text-label text-text-secondary text-center animate-fade-in animate-delay-100">This may take a moment</p>
						{:else}
							<div class="h-20 w-20 rounded-3xl bg-surface-0 dark:bg-surface-700 ring-1 ring-primary-200 dark:ring-primary-800 flex items-center justify-center">
								<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-500 dark:text-primary-400"><path d="m23 19-7-16 2v-8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8"/><path d="M16 3h5"/><path d="M21 14V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9"/><path d="M21 14v7"/></svg>
							</div>
							<p class="mt-4 text-body font-semibold">Tap to scan</p>
							<p class="mt-1 text-label text-text-secondary text-center">Or upload a photo/PDF of your receipt</p>
						{/if}
					</div>
				</div>
			</div>

			<div class="flex gap-3 mt-4">
				<button
					type="button"
					onclick={handleOpenCamera}
					disabled={loading}
					class="flex-1 h-12 min-h-[44px] rounded-2xl bg-primary-500 shadow-md flex items-center justify-center gap-2 text-text-inverted font-semibold active:scale-[0.99] focus-visible:ring-2 focus-visible:ring-primary-500/50 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-inverted"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
					<span class="text-label">Open Camera</span>
				</button>

				<div class="relative flex-1">
					<input
						type="file"
						id="receipt-upload"
						accept="image/jpeg,image/png,image/webp,application/pdf"
						onchange={handleFileUpload}
						class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
						disabled={loading}
						aria-label="Upload receipt image"
					/>
					<button
						type="button"
						disabled={loading}
						class="w-full h-12 min-h-[44px] rounded-2xl bg-surface-0 dark:bg-surface-700 border border-surface-200 dark:border-surface-600 shadow-md flex items-center justify-center gap-2 text-text-primary dark:text-text-inverted font-semibold active:scale-[0.99] focus-visible:ring-2 focus-visible:ring-primary-500 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-primary"><path d="m21 15-4 4-4"/><path d="M17 8h-4"/><path d="m21 3-5 7-7-5"/><path d="M3 3v18h18"/></svg>
						<span class="text-label">Upload File</span>
					</button>
				</div>
			</div>

			<div class="flex justify-center gap-3 mt-4">
				<div class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-0 shadow-sm border border-surface-200">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-500"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
					<span class="text-caption font-semibold text-text-primary">Auto-detect totals</span>
				</div>
				<div class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-0 shadow-sm border border-surface-200">
					<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-success"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
					<span class="text-caption font-semibold text-text-primary">Private by default</span>
				</div>
			</div>
		</section>

		<section class="mt-section rounded-3xl bg-surface-0 shadow-card border border-surface-200" aria-label="Item details">
			<div class="px-4 py-3 bg-surface-50 dark:bg-surface-700/50 flex items-center justify-between">
				<div class="flex items-center gap-2">
					<div class="h-5 w-5 rounded-full bg-success flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-inverted"><path d="M20 6 9 17 4 18"/><path d="m4 18 9-17"/></svg>
					</div>
					<span class="text-caption font-bold text-text-primary uppercase tracking-wider">Scan Complete</span>
				</div>
				<div class="flex items-center gap-1.5 rounded-full bg-success/10 dark:bg-success/20 px-2 py-1 ring-1 ring-success/20 dark:ring-success/30">
					<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-success dark:text-success/80"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
					<span class="text-caption font-bold text-success">98% Confidence</span>
				</div>
			</div>

			<div class="p-4">
				<div class="space-y-component">
					{#each items as item, index}
						{@const itemErrors = validationErrors.filter(e => e.itemId === item.id)}
						<div class="flex items-center gap-3 {itemErrors.length > 0 ? 'bg-error/5 dark:bg-error/10 rounded-xl p-2 -m-2 animate-shake' : 'animate-slide-in-right'}" style="animation-delay: {Math.min(index * 50, 200)}ms;">
							<button
								type="button"
								class="h-11 w-11 min-h-[44px] min-w-[44px] rounded-full bg-surface-100 dark:bg-surface-700 flex items-center justify-center hover:bg-error/10 dark:hover:bg-error/20 hover:text-error dark:hover:text-error/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed active:scale-90 transition-transform duration-150"
								onclick={() => handleRemoveItem(item.id)}
								aria-label="Remove {item.name || 'item ' + (index + 1)}"
								disabled={items.length <= 1 || loading}
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
							</button>
							<div class="flex-1 min-w-0">
								<input
									type="text"
									value={item.name}
									oninput={(e) => handleItemNameChange(item.id, e.currentTarget.value)}
									class="w-full border-none bg-transparent p-0 text-label font-semibold text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-sm {itemErrors.some(e => e.message.includes('name')) ? 'text-error' : ''}"
									placeholder="Item name"
									maxlength="100"
									aria-invalid={itemErrors.some(e => e.message.includes('name'))}
									aria-describedby={'item-name-' + item.id}
								/>
								{#if itemErrors.some(e => e.message.includes('name'))}
									<p id={'item-name-' + item.id} class="text-caption text-error mt-1">
										{itemErrors.find(e => e.message.includes('name'))?.message}
									</p>
								{/if}
							</div>
							<div class="flex items-center gap-1">
								<span class="text-caption text-text-tertiary">$</span>
								<input
									type="number"
									value={item.price === 0 ? '' : item.price}
									oninput={(e) => handleItemPriceChange(item.id, e.currentTarget.value)}
									class="w-20 border-none bg-transparent p-0 text-right text-label font-bold text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-sm tabular-nums {itemErrors.some(e => e.message.includes('Price')) ? 'text-error' : ''}"
									placeholder="0.00"
									step="0.01"
									min="0"
									max="999999.99"
									aria-invalid={itemErrors.some(e => e.message.includes('Price'))}
									aria-describedby={'item-price-' + item.id}
								/>
							</div>
						</div>
						{#if itemErrors.some(e => e.message.includes('Price')) && !itemErrors.some(e => e.message.includes('name'))}
							<p id={'item-price-' + item.id} class="text-caption text-error ml-14 -mt-1">
								{itemErrors.find(e => e.message.includes('Price'))?.message}
							</p>
						{/if}
					{/each}

					<div class="pt-1 flex items-center justify-between">
						<button
							type="button"
							onclick={handleAddItem}
							class="flex items-center gap-1.5 text-caption font-bold text-primary-500 dark:text-primary-400"
						>
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/></svg>
							Add Item
						</button>
						<span class="text-caption font-medium text-text-tertiary">Subtotal: ${subtotal.toFixed(2)}</span>
					</div>
				</div>

				<div class="mt-4 pt-4 border-t border-surface-100 dark:border-surface-700 space-y-component">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<div class="h-7 w-7 rounded-lg bg-warning/10 dark:bg-warning/20 flex items-center justify-center text-warning">
								<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 1 0 7h5a3.5 3.5 0 0 1 0 7H17"/></svg>
							</div>
							<div class="leading-none">
								<p class="text-caption font-bold text-text-primary">Tax Detected: {taxDetected}%</p>
								<button class="text-caption font-medium text-primary-500 dark:text-primary-400 underline decoration-primary-200 dark:decoration-primary-800 underline-offset-2 mt-0.5">Edit Rate</button>
							</div>
						</div>
						<button type="button" class="relative h-6 w-10 rounded-full bg-primary-500 dark:bg-primary-600 focus-visible:ring-2 focus-visible:ring-primary-500/50 focus-visible:ring-offset-2" role="switch" aria-checked="true" aria-label="Toggle tax">
							<span class="absolute right-1 top-1 h-4 w-4 rounded-full bg-surface-0"></span>
						</button>
					</div>

					<div class="flex items-center justify-between rounded-xl bg-surface-50 dark:bg-surface-700/50 p-3 border border-surface-100 dark:border-surface-600">
						<span class="text-label font-semibold text-text-secondary">Total Amount</span>
						<div class="flex items-baseline gap-1">
							<span class="text-caption font-bold text-text-tertiary">USD</span>
							<span class="text-subheading font-bold text-text-primary tabular-nums">${totalAmount.toFixed(2)}</span>
						</div>
					</div>
				</div>

				<div class="mt-5 grid grid-cols-2 gap-component">
					<button
						type="button"
						onclick={handleShare}
						disabled={loading || items.length === 0}
						class="flex h-10 items-center justify-center gap-2 rounded-xl bg-surface-0 text-caption font-bold text-text-primary shadow-sm border border-surface-200 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
						Share
					</button>
					<button
						type="button"
						onclick={handleConfirm}
						disabled={loading}
						class="flex h-10 items-center justify-center gap-2 rounded-xl bg-primary-500 dark:bg-primary-600 text-caption font-bold text-text-inverted shadow-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-600 dark:hover:bg-primary-700 active:scale-95 transition-all duration-150 group"
					>
						{#if loading}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="14"
								height="14"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								class="animate-spin"
							>
								<path d="M21 12a9 9 0 1 1-6.219-8.56" />
							</svg>
							<span class="ml-1">Processing...</span>
						{:else}
							<span class="group-hover:hidden">Confirm</span>
							<span class="hidden group-hover:inline">Proceed</span>
							<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="group-hover:translate-x-0.5 transition-transform"><path d="M5 12h14"/><path d="m12 5 7 7-7"/></svg>
						{/if}
					</button>
				</div>
			</div>
		</section>

		<section class="mt-section rounded-3xl bg-primary-50 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-800" aria-label="Tips and help">
			<div class="p-4">
				<div class="flex items-start gap-3">
					<div class="h-11 w-11 rounded-2xl bg-surface-0 dark:bg-surface-700 border border-primary-200 dark:border-primary-800 flex items-center justify-center">
						<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-500 dark:text-primary-400"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
					</div>
					<div class="flex-1">
						<p class="text-label font-semibold dark:text-text-inverted">Tips for best results</p>
						<ul class="mt-2 space-y-2 text-label text-text-primary">
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
						<div class="mt-4 flex gap-component">
							<a href="#learn-more" class="h-11 px-4 inline-flex items-center justify-center rounded-2xl bg-surface-0 dark:bg-surface-700 border border-primary-200 dark:border-primary-800 text-label font-semibold text-primary-600 dark:text-primary-300 shadow-md">
								Learn more
							</a>
							<a href="#troubleshoot" class="h-11 px-4 inline-flex items-center justify-center rounded-2xl bg-primary-500 dark:bg-primary-600 text-label font-semibold text-text-inverted shadow-md">
								Troubleshoot
							</a>
						</div>
					</div>
				</div>
			</div>
		</section>
	</main>
</div>
