<script lang="ts">
	import { onMount } from 'svelte';
	import { currencyStore } from '$lib/stores';

	let darkMode = $state(false);
	let notifications = $state(true);
	let soundEffects = $state(true);
	let selectedCurrency = $state('IDR');

	// Watch for changes and persist to localStorage
	$effect(() => {
		localStorage.setItem('darkMode', String(darkMode));
		if (darkMode) {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	});

	$effect(() => {
		localStorage.setItem('notifications', String(notifications));
	});

	$effect(() => {
		localStorage.setItem('soundEffects', String(soundEffects));
	});

	onMount(() => {
		const savedDarkMode = localStorage.getItem('darkMode');
		const savedNotifications = localStorage.getItem('notifications');
		const savedSoundEffects = localStorage.getItem('soundEffects');

		if (savedDarkMode) darkMode = savedDarkMode === 'true';
		if (darkMode) document.documentElement.classList.add('dark');
		if (savedNotifications) notifications = savedNotifications === 'true';
		if (savedSoundEffects) soundEffects = savedSoundEffects === 'true';

		currencyStore.init().catch(() => {});
	});

	function copyAPIKey() {
		const apiKey = 'sb_live_24x9••••••••••••••••••••R7';
		navigator.clipboard.writeText(apiKey).then(() => {
			alert('API key copied to clipboard!');
		});
	}

	function handleExport() {
		alert('Exporting data...');
	}

	function handleClearCache() {
		if (confirm('Are you sure you want to clear the cache? This will keep your split history.')) {
			indexedDB.deleteDatabase('split-bill-offline');
			alert('Cache cleared successfully!');
		}
	}
</script>

<svelte:head>
	<title>Settings - Split Bill</title>
	<meta name="view-transition" content="same-origin" />
</svelte:head>

<div class="w-full min-h-dvh flex flex-col bg-slate-50 text-slate-900">
	<!-- Header -->
	<header class="shrink-0 pt-14 px-4">
		<div class="flex items-start justify-between gap-3">
			<div class="min-w-0">
				<p class="text-xs font-semibold tracking-wide text-sky-700">Split Bill</p>
				<h1 class="mt-1 text-2xl font-extrabold tracking-tight">Settings</h1>
				<p class="mt-1 text-sm text-slate-600">Manage your groups, data, and account.</p>
			</div>
			<div class="shrink-0">
				<div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center shadow-md">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0-.73 2.73l.08.15a2 2 0 0 1 0 2l-.08.15a2 2 0 0 0 .73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 0 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.08-.14a2 2 0 0 1 0-2l.08-.15a2 2 0 0 0-.73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
				</div>
			</div>
		</div>

		<!-- Accent strip -->
		<div class="mt-4 rounded-3xl bg-gradient-to-r from-sky-200 via-sky-100 to-white p-[2px] shadow-md">
			<div class="rounded-[22px] bg-white px-4 py-3 flex items-center gap-3">
				<div class="h-10 w-10 rounded-2xl bg-sky-500 text-white flex items-center justify-center shadow-md">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3l-5.8 1.9 5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3l5.8-1.9-5.8-1.9a2 2 0 0 1-1.3-1.3z"/></svg>
				</div>
				<div class="min-w-0">
					<p class="text-sm font-semibold">Keep it smooth</p>
					<p class="text-xs text-slate-600">Changes save automatically on this device.</p>
				</div>
			</div>
		</div>
	</header>

	<!-- Main -->
	<main class="flex-1 overflow-y-auto px-4 pt-6 pb-28">
		<!-- General / Currency -->
		<section aria-label="General" class="mb-6">
			<div class="flex items-center justify-between px-1">
				<h2 class="text-xs font-bold tracking-wider text-slate-500 uppercase">General</h2>
				<span class="text-xs text-slate-500">Region & locale</span>
			</div>

			<div class="mt-2 rounded-3xl bg-white shadow-md ring-1 ring-slate-100 overflow-hidden relative">
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78"/><path d="M17.5 11c0 3.03-2.76 5.5-6.5 5.5S4.5 14.03 4.5 11"/><path d="M12 16.5v4"/><path d="M8 21h8"/></svg>
						</div>
						<div>
							<p class="text-sm font-semibold text-slate-900">Currency</p>
							<p class="text-xs text-slate-600">Default for new expenses.</p>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<span class="text-sm font-semibold text-sky-600">IDR (Rp)</span>
						<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
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
		<section aria-label="Preferences" class="mb-6">
			<div class="flex items-center justify-between px-1">
				<h2 class="text-xs font-bold tracking-wider text-slate-500 uppercase">Preferences</h2>
				<span class="text-xs text-slate-500">Appearance & alerts</span>
			</div>

			<div class="mt-2 rounded-3xl bg-white shadow-md ring-1 ring-slate-100 overflow-hidden">
				<!-- Dark mode -->
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3 min-w-0">
						<div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
						</div>
						<div class="min-w-0">
							<p class="text-sm font-semibold">Dark mode</p>
							<p class="text-xs text-slate-600">Use a darker theme at night.</p>
						</div>
					</div>
					<label class="shrink-0 inline-flex items-center justify-center h-11" aria-label="Toggle dark mode">
						<input type="checkbox" class="peer sr-only" bind:checked={darkMode} />
						<span class="relative inline-flex h-7 w-12 items-center rounded-full bg-slate-200 transition-colors peer-checked:bg-sky-500">
							<span class="absolute left-1 top-1 h-5 w-5 rounded-full bg-white shadow-md transition-transform peer-checked:translate-x-5"></span>
						</span>
					</label>
				</div>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- Notifications -->
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3 min-w-0">
						<div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
						</div>
						<div class="min-w-0">
							<p class="text-sm font-semibold">Notifications</p>
							<p class="text-xs text-slate-600">Get reminders for unpaid splits.</p>
						</div>
					</div>
					<label class="shrink-0 inline-flex items-center justify-center h-11" aria-label="Toggle notifications">
						<input type="checkbox" class="peer sr-only" bind:checked={notifications} />
						<span class="relative inline-flex h-7 w-12 items-center rounded-full bg-slate-200 transition-colors peer-checked:bg-sky-500">
							<span class="absolute left-1 top-1 h-5 w-5 rounded-full bg-white shadow-md transition-transform peer-checked:translate-x-5"></span>
						</span>
					</label>
				</div>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- Sound -->
				<div class="px-4 py-4 flex items-center justify-between gap-4">
					<div class="flex items-center gap-3 min-w-0">
						<div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H2a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1h4l5 4V5Z"/><path d="m15.54 8.46 5-5"/><path d="M20.5 13.5 16 9"/></svg>
						</div>
						<div class="min-w-0">
							<p class="text-sm font-semibold">Sound effects</p>
							<p class="text-xs text-slate-600">Play sounds on interactions.</p>
						</div>
					</div>
					<label class="shrink-0 inline-flex items-center justify-center h-11" aria-label="Toggle sound">
						<input type="checkbox" class="peer sr-only" bind:checked={soundEffects} />
						<span class="relative inline-flex h-7 w-12 items-center rounded-full bg-slate-200 transition-colors peer-checked:bg-sky-500">
							<span class="absolute left-1 top-1 h-5 w-5 rounded-full bg-white shadow-md transition-transform peer-checked:translate-x-5"></span>
						</span>
					</label>
				</div>
			</div>
		</section>

		<!-- Social -->
		<section aria-label="Social" class="mb-6">
			<div class="flex items-center justify-between px-1">
				<h2 class="text-xs font-bold tracking-wider text-slate-500 uppercase">Social</h2>
				<span class="text-xs text-slate-500">Groups & payments</span>
			</div>
			<div class="mt-2 rounded-3xl bg-white shadow-md ring-1 ring-slate-100 overflow-hidden">
				<!-- Manage Groups -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-slate-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
						</div>
						<div class="text-left">
							<p class="text-sm font-semibold text-slate-900">Manage groups</p>
							<p class="text-xs text-slate-600">Edit members and roles.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- Payment Methods -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-slate-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
						</div>
						<div class="text-left">
							<p class="text-sm font-semibold text-slate-900">Payment methods</p>
							<p class="text-xs text-slate-600">Linked cards and wallets.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>

				<div class="h-px bg-slate-100 mx-4"></div>

				<!-- Sharing -->
				<button type="button" class="w-full px-4 py-4 flex items-center justify-between gap-4 active:bg-slate-50 transition-colors">
					<div class="flex items-center gap-3">
						<div class="h-11 w-11 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
						</div>
						<div class="text-left">
							<p class="text-sm font-semibold text-slate-900">Sharing preferences</p>
							<p class="text-xs text-slate-600">Default invite settings.</p>
						</div>
					</div>
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-400"><path d="m9 18 6-6"/><path d="m15 18-6-6"/></svg>
				</button>
			</div>
		</section>

		<!-- Data -->
		<section aria-label="Data" class="mb-6">
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
						<button type="button" onclick={handleExport} class="h-11 px-4 rounded-2xl bg-sky-500 text-white text-sm font-semibold shadow-md active:scale-[0.99] transition-transform whitespace-nowrap">
							Export
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
						<button type="button" onclick={handleClearCache} class="h-11 px-4 rounded-2xl bg-white text-rose-600 text-sm font-semibold ring-1 ring-rose-200 shadow-sm active:scale-[0.99] transition-transform whitespace-nowrap">
							Clear
						</button>
					</div>
				</div>
			</div>
		</section>

		<!-- Account -->
		<section aria-label="Account">
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
								class="h-11 w-full rounded-2xl bg-slate-50 px-3 text-sm text-slate-700 ring-1 ring-slate-200 focus:outline-none"
							/>
							<button
								type="button"
								onclick={copyAPIKey}
								class="h-11 w-11 rounded-2xl bg-white ring-1 ring-slate-200 shadow-sm flex items-center justify-center active:scale-[0.99] transition-transform"
								aria-label="Copy API key"
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-700"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2v2"/></svg>
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
