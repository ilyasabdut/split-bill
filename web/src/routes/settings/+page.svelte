<script lang="ts">
	import { onMount } from 'svelte';
	import { currencyStore } from '$lib/stores';
	import ErrorMessage from '$lib/components/ui/ErrorMessage.svelte';

	let darkMode = $state(false);
	let notifications = $state(true);
	let soundEffects = $state(true);
	let selectedCurrency = $state('IDR');
	let storageError = $state<string | null>(null);
	let copySuccess = $state(false);
	let clearSuccess = $state(false);

	// Safe localStorage operations with error handling
	function saveToStorage(key: string, value: string): boolean {
		try {
			localStorage.setItem(key, value);
			storageError = null;
			return true;
		} catch (err) {
			if (err instanceof Error && err.name === 'QuotaExceededError') {
				storageError = 'Storage is full. Please clear some data to save settings.';
			} else {
				storageError = 'Failed to save settings. Please try again.';
			}
			return false;
		}
	}

	function loadFromStorage(key: string): string | null {
		try {
			return localStorage.getItem(key);
		} catch (err) {
			console.error('Failed to load from storage:', err);
			return null;
		}
	}

	// Watch for changes and persist to localStorage
	$effect(() => {
		if (darkMode) {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
		saveToStorage('darkMode', String(darkMode));
	});

	$effect(() => {
		saveToStorage('notifications', String(notifications));
	});

	$effect(() => {
		saveToStorage('soundEffects', String(soundEffects));
	});

	onMount(() => {
		const savedDarkMode = loadFromStorage('darkMode');
		const savedNotifications = loadFromStorage('notifications');
		const savedSoundEffects = loadFromStorage('soundEffects');

		if (savedDarkMode !== null) darkMode = savedDarkMode === 'true';
		if (savedNotifications !== null) notifications = savedNotifications === 'true';
		if (savedSoundEffects !== null) soundEffects = savedSoundEffects === 'true';

		// Apply dark mode from saved state
		if (darkMode) document.documentElement.classList.add('dark');

		currencyStore.init().catch((err) => {
			console.error('Failed to initialize currency:', err);
		});
	});

	async function copyAPIKey() {
		const apiKey = 'sb_live_24x9••••••••••••••••••••R7';

		try {
			await navigator.clipboard.writeText(apiKey);
			copySuccess = true;
			setTimeout(() => copySuccess = false, 2000);
		} catch (err) {
			storageError = 'Failed to copy API key. Please copy manually.';
		}
	}

	async function handleExport() {
		try {
			// Simulate export - in real app, this would generate CSV/JSON
			const data = JSON.stringify({
				settings: { darkMode, notifications, soundEffects },
				exportDate: new Date().toISOString()
			}, null, 2);

			const blob = new Blob([data], { type: 'application/json' });
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `split-bill-export-${new Date().toISOString().split('T')[0]}.json`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
		} catch (err) {
			storageError = 'Failed to export data. Please try again.';
		}
	}

	async function handleClearCache() {
		try {
			// Clear IndexedDB
			await new Promise<void>((resolve, reject) => {
				const request = indexedDB.deleteDatabase('split-bill-offline');
				request.onsuccess = () => resolve();
				request.onerror = () => reject(request.error);
			});

			clearSuccess = true;
			setTimeout(() => clearSuccess = false, 3000);
		} catch (err) {
			storageError = 'Failed to clear cache. Please try again.';
		}
	}
</script>

<svelte:head>
	<title>Settings - Split Bill</title>
	<meta name="view-transition" content="same-origin" />
</svelte:head>

<div class="w-full min-h-dvh flex flex-col bg-surface-50 text-text-primary">
	<!-- Header -->
	<header class="shrink-0 pt-14 px-4">
		<div class="flex items-start justify-between gap-3">
			<div class="min-w-0">
				<p class="text-caption font-semibold tracking-wide text-primary-500">Split Bill</p>
				<h1 class="mt-1 text-heading font-extrabold tracking-tight">Settings</h1>
				<p class="mt-1 text-label text-text-secondary">Manage your groups, data, and account.</p>
			</div>
			<div class="shrink-0">
				<div class="h-11 w-11 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center shadow-card">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0-.73 2.73l.08.15a2 2 0 0 1 0 2l-.08.15a2 2 0 0 0 .73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 0 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.08-.14a2 2 0 0 1 0-2l.08-.15a2 2 0 0 0-.73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
				</div>
			</div>
		</div>

		<!-- Accent strip -->
		<div class="mt-4 rounded-3xl bg-gradient-to-r from-primary-200 via-primary-100 to-surface-0 p-[2px] shadow-card">
			<div class="rounded-[22px] bg-surface-0 px-4 py-3 flex items-center gap-3">
				<div class="h-10 w-10 rounded-2xl bg-primary-500 text-text-inverted flex items-center justify-center shadow-card">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
				</div>
				<div class="min-w-0">
					<p class="text-label font-semibold">Keep it smooth</p>
					<p class="text-caption text-text-secondary">Changes save automatically on this device.</p>
				</div>
			</div>
		</div>
	</header>

	<!-- Main -->
	<main class="flex-1 overflow-y-auto px-4 pt-6 pb-28">
		<!-- Error Message -->
		{#if storageError}
			<ErrorMessage
				message={storageError}
				onDismiss={() => storageError = null}
				variant="inline"
			/>
		{/if}

		<!-- General / Currency -->
		<section aria-label="General" class="mb-section animate-slide-up">
			<div class="flex items-center justify-between px-1">
				<h2 class="text-caption font-bold tracking-wider text-text-tertiary uppercase">General</h2>
				<span class="text-caption text-text-tertiary">Region & locale</span>
			</div>

			<div class="mt-2 rounded-3xl bg-surface-0 shadow-card border border-surface-100 overflow-hidden relative">
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78"/><path d="M17.5 11c0 3.03-2.76 5.5-6.5 5.5S4.5 14.03 4.5 11"/><path d="M12 16.5v4"/><path d="M8 21h8"/></svg>
						</div>
						<div>
							<p class="text-label font-semibold text-text-primary">Currency</p>
							<p class="text-caption text-text-secondary">Default for new expenses.</p>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<span class="text-label font-semibold text-primary-500">IDR (Rp)</span>
						<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
					</div>
					<select class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" aria-label="Select currency">
						<option value="USD">USD ($)</option>
						<option value="NZD">NZD ($)</option>
						<option value="JPY">YEN (¥)</option>
						<option value="IDR" selected>IDR (Rp)</option>
					</select>
				</div>
			</div>
		</section>

		<!-- Preferences -->
		<section aria-label="Preferences" class="mb-section animate-slide-up" style="animation-delay: 100ms;">
			<div class="flex items-center justify-between px-1">
				<h2 class="text-caption font-bold tracking-wider text-text-tertiary uppercase">Preferences</h2>
				<span class="text-caption text-text-tertiary">Appearance & alerts</span>
			</div>

			<div class="mt-2 rounded-3xl bg-surface-0 shadow-card border border-surface-100 overflow-hidden">
				<!-- Dark mode -->
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3 min-w-0">
						<div class="h-11 w-11 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
						</div>
						<div class="min-w-0">
							<p class="text-label font-semibold">Dark mode</p>
							<p class="text-caption text-text-secondary">Use a darker theme at night.</p>
						</div>
					</div>
					<label class="shrink-0 inline-flex items-center justify-center h-11" aria-label="Toggle dark mode">
						<input type="checkbox" class="peer sr-only" bind:checked={darkMode} />
						<span class="relative inline-flex h-7 w-12 items-center rounded-full bg-surface-200 transition-colors peer-checked:bg-primary-500">
							<span class="absolute left-1 top-1 h-5 w-5 rounded-full bg-surface-0 shadow-md transition-transform peer-checked:translate-x-5"></span>
						</span>
					</label>
				</div>

				<div class="h-px bg-surface-100 mx-4"></div>

				<!-- Notifications -->
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3 min-w-0">
						<div class="h-11 w-11 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
						</div>
						<div class="min-w-0">
							<p class="text-label font-semibold">Notifications</p>
							<p class="text-caption text-text-secondary">Get reminders for unpaid splits.</p>
						</div>
					</div>
					<label class="shrink-0 inline-flex items-center justify-center h-11" aria-label="Toggle notifications">
						<input type="checkbox" class="peer sr-only" bind:checked={notifications} />
						<span class="relative inline-flex h-7 w-12 items-center rounded-full bg-surface-200 transition-colors peer-checked:bg-primary-500">
							<span class="absolute left-1 top-1 h-5 w-5 rounded-full bg-surface-0 shadow-md transition-transform peer-checked:translate-x-5"></span>
						</span>
					</label>
				</div>

				<div class="h-px bg-surface-100 mx-4"></div>

				<!-- Sound -->
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3 min-w-0">
						<div class="h-11 w-11 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H2a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1h4l5 4V5Z"/><path d="m15.54 8.46 5-5"/><path d="M20.5 13.5 16 9"/></svg>
						</div>
						<div class="min-w-0">
							<p class="text-label font-semibold">Sound effects</p>
							<p class="text-caption text-text-secondary">Play sounds on interactions.</p>
						</div>
					</div>
					<label class="shrink-0 inline-flex items-center justify-center h-11" aria-label="Toggle sound">
						<input type="checkbox" class="peer sr-only" bind:checked={soundEffects} />
						<span class="relative inline-flex h-7 w-12 items-center rounded-full bg-surface-200 transition-colors peer-checked:bg-primary-500">
							<span class="absolute left-1 top-1 h-5 w-5 rounded-full bg-surface-0 shadow-md transition-transform peer-checked:translate-x-5"></span>
						</span>
					</label>
				</div>
			</div>
		</section>

		<!-- Social -->
		<section aria-label="Social" class="mb-section animate-slide-up" style="animation-delay: 200ms;">
			<div class="flex items-center justify-between px-1">
				<h2 class="text-caption font-bold tracking-wider text-text-tertiary uppercase">Social</h2>
				<span class="text-caption text-text-tertiary">Groups & payments</span>
			</div>
			<div class="mt-2 rounded-3xl bg-surface-0 shadow-card border border-surface-100 overflow-hidden">
				<!-- Manage Groups -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-surface-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-500 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
						</div>
						<div class="text-left">
							<p class="text-label font-semibold text-text-primary">Manage groups</p>
							<p class="text-caption text-text-secondary">Edit members and roles.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>

				<div class="h-px bg-surface-100 mx-4"></div>

				<!-- Payment Methods -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-surface-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-500 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
						</div>
						<div class="text-left">
							<p class="text-label font-semibold text-text-primary">Payment methods</p>
							<p class="text-caption text-text-secondary">Linked cards and wallets.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>

				<div class="h-px bg-surface-100 mx-4"></div>

				<!-- Sharing -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-surface-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-500 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
						</div>
						<div class="text-left">
							<p class="text-label font-semibold text-text-primary">Sharing preferences</p>
							<p class="text-caption text-text-secondary">Default invite settings.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-tertiary"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>
			</div>
		</section>

		<!-- Data -->
		<section aria-label="Data" class="mb-6 animate-slide-up" style="animation-delay: 300ms;">
			<div class="flex items-center justify-between px-1">
				<h2 class="text-xs font-bold tracking-wider text-slate-500 uppercase">Data</h2>
				<span class="text-xs text-slate-500">Export & insights</span>
			</div>

			<div class="mt-2 rounded-3xl bg-white shadow-md ring-1 ring-slate-100 overflow-hidden">
				<!-- Monthly Summary -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-slate-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="9" y1="14" x2="15" y2="14"/></svg>
						</div>
						<div class="text-left">
							<p class="text-sm font-semibold text-slate-900">Monthly summary</p>
							<p class="text-xs text-slate-600">Spending breakdown.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- Analytics -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-slate-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
						</div>
						<div class="text-left">
							<p class="text-sm font-semibold text-slate-900">Analytics</p>
							<p class="text-xs text-slate-600">Visual charts & trends.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- Export CSV -->
				<div class="px-4 py-4">
					<div class="flex items-start justify-between gap-4">
						<div class="flex items-center gap-3 min-w-0">
							<div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
							</div>
							<div class="min-w-0">
								<p class="text-sm font-semibold">Export CSV</p>
								<p class="text-xs text-slate-600">Download your split history.</p>
							</div>
						</div>
						<button type="button" onclick={handleExport} class="h-11 px-4 rounded-2xl bg-sky-500 text-white text-label font-semibold shadow-md active:scale-[0.99] transition-transform whitespace-nowrap hover:bg-sky-600">
							<span class="truncate">Export</span>
						</button>
					</div>
				</div>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- Clear cache -->
				<div class="px-4 py-4">
					<div class="flex items-start justify-between gap-4">
						<div class="flex items-center gap-3 min-w-0">
							<div class="h-11 w-11 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center">
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
							</div>
							<div class="min-w-0">
								<p class="text-sm font-semibold">Clear cache</p>
								<p class="text-xs text-slate-600">Frees space (keeps splits).</p>
							</div>
						</div>
						<div class="flex items-center gap-2">
							{#if clearSuccess}
								<span class="text-caption font-semibold text-success">Cleared!</span>
							{/if}
							<button type="button" onclick={handleClearCache} class="h-11 px-4 rounded-2xl bg-white text-rose-600 text-label font-semibold ring-1 ring-rose-200 shadow-sm active:scale-[0.99] transition-transform whitespace-nowrap hover:bg-rose-50">
								<span class="truncate">Clear</span>
							</button>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Account -->
		<section aria-label="Account" class="animate-slide-up" style="animation-delay: 400ms;">
			<div class="flex items-center justify-between px-1">
				<h2 class="text-xs font-bold tracking-wider text-slate-500 uppercase">Account</h2>
				<span class="text-xs text-slate-500">Access & Privacy</span>
			</div>

			<div class="mt-2 rounded-3xl bg-white shadow-md ring-1 ring-slate-100 overflow-hidden">
				<!-- Privacy Settings -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-slate-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-slate-100 text-slate-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
						</div>
						<div class="text-left">
							<p class="text-sm font-semibold text-slate-900">Privacy settings</p>
							<p class="text-xs text-slate-600">Manage data visibility.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- API key -->
				<div class="px-4 py-4">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 18a3 3 0 0 1 3-3h4a2 2 0 0 0 2-2V9a1 1 0 0 1 1-1h3a2 2 0 0 0 2 2v6a2 2 0 0 0 2 2h4a3 3 0 0 1 3 3v1a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-1Z"/><circle cx="8" cy="5" r="1"/><circle cx="18" cy="5" r="1"/></svg>
						</div>
						<div class="min-w-0">
							<p class="text-sm font-semibold">API key</p>
							<p class="text-xs text-slate-600">Used for receipt scanning integrations.</p>
						</div>
					</div>

					<div class="mt-3">
						<label class="block text-xs font-semibold text-slate-600 mb-2" for="api-key">Key</label>
						<div class="flex items-stretch gap-2">
							<input
								id="api-key"
								type="text"
								readonly
								value="sb_live_24x9•••••••••••••R7"
								class="h-11 w-full rounded-2xl bg-slate-50 px-3 text-sm text-slate-700 ring-1 ring-slate-200 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
							/>
							<button
								type="button"
								onclick={copyAPIKey}
								class="h-11 min-w-[44px] rounded-2xl {copySuccess ? 'bg-success text-white animate-pulse-success' : 'bg-white ring-1 ring-slate-200 hover:bg-slate-50'} ring-1 ring-slate-200 shadow-sm flex items-center justify-center active:scale-[0.99] transition-all duration-200"
								aria-label="Copy API key"
							>
								{#if copySuccess}
									<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
								{:else}
									<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2v2"/></svg>
								{/if}
							</button>
						</div>
					</div>
				</div>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- App Version -->
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-slate-50 text-slate-400 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
						</div>
						<div>
							<p class="text-sm font-semibold text-slate-900">App version</p>
							<p class="text-xs text-slate-600">Build 2023.10.42</p>
						</div>
					</div>
					<span class="text-xs font-medium text-slate-400 bg-slate-100 px-2 py-1 rounded-lg">v2.4.0</span>
				</div>
			</div>
		</section>

		<!-- Footer note -->
		<div class="mt-6 rounded-3xl bg-sky-50 ring-1 ring-sky-100 px-4 py-3">
			<div class="flex items-start gap-3">
				<div class="mt-0.5 h-8 w-8 rounded-2xl bg-sky-500 text-white flex items-center justify-center shadow-md">
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
				</div>
				<div class="min-w-0">
					<p class="text-sm font-semibold text-slate-900">Privacy-first</p>
					<p class="text-xs text-slate-600">Your splits stay on your device unless you share them.</p>
				</div>
			</div>
		</div>
	</main>
</div>
