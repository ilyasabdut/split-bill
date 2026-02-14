<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import CurrencySelector from '$lib/components/CurrencySelector.svelte';
  import { currencyStore, analyticsStore } from '$lib/stores';
  import { goto } from '$app/navigation';

  let darkMode = $state(false);
  let notifications = $state(true);
  let soundEffects = $state(true);
  let clearingCache = $state(false);

  onMount(async () => {
    // Load settings from localStorage
    const savedDarkMode = localStorage.getItem('darkMode');
    const savedNotifications = localStorage.getItem('notifications');
    const savedSoundEffects = localStorage.getItem('soundEffects');

    if (savedDarkMode) darkMode = savedDarkMode === 'true';
    if (savedNotifications) notifications = savedNotifications === 'true';
    if (savedSoundEffects) soundEffects = savedSoundEffects === 'true';

    await currencyStore.init();
  });

  function handleSaveSettings() {
    // Save settings to localStorage
    localStorage.setItem('darkMode', String(darkMode));
    localStorage.setItem('notifications', String(notifications));
    localStorage.setItem('soundEffects', String(soundEffects));

    // Apply dark mode
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    alert('Settings saved successfully!');
  }

  function handleExportCSV() {
    analyticsStore.exportData('csv');
  }

  function handleClearCache() {
    if (confirm('Are you sure you want to clear the cache? This will keep your split history.')) {
      // Clear IndexedDB
      indexedDB.deleteDatabase('split-bill-offline');
      alert('Cache cleared successfully!');
    }
  }

  function copyAPIKey() {
    const apiKey = 'sb_live_24x9•••••••••••••••••••R7';
    navigator.clipboard.writeText(apiKey).then(() => {
      alert('API key copied to clipboard!');
    }).catch(() => {
      alert('Failed to copy API key');
    });
  }
</script>

<svelte:head>
  <title>Settings - Split Bill</title>
</svelte:head>

<div class="space-y-6 pb-[60px]">
  <!-- Header -->
  <header class="pt-12 px-4 pb-2">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center shadow-md">
          <span class="text-xl">⚙️</span>
        </div>
        <div>
          <p class="text-xs font-bold text-sky-700 tracking-wide uppercase">Split Bill</p>
          <h1 class="text-2xl font-extrabold tracking-tight">Settings</h1>
          <p class="text-sm text-slate-600">Manage your groups, data, and account.</p>
        </div>
      </div>
    </div>
  </header>

  <!-- General Section -->
  <section aria-label="General" class="px-4">
    <div class="flex items-center justify-between mb-2">
      <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider">General</h2>
      <span class="text-xs text-slate-500">Region & locale</span>
    </div>

    <Card>
      <div class="px-4 py-3 flex items-center justify-between bg-slate-50/50">
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
            <span class="text-lg">💰</span>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-900">Currency</p>
            <p class="text-xs text-slate-600">Default for new expenses.</p>
          </div>
        </div>
        <CurrencySelector />
      </div>
    </Card>
  </section>

  <!-- Preferences Section -->
  <section aria-label="Preferences" class="px-4 mt-6">
    <div class="flex items-center justify-between mb-2">
      <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Preferences</h2>
      <span class="text-xs text-slate-500">Appearance & alerts</span>
    </div>

    <Card padding="none">
      <!-- Dark Mode -->
      <div class="px-4 py-4 flex items-center justify-between border-b border-slate-100">
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
            <span class="text-lg">🌙</span>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-900">Dark mode</p>
            <p class="text-xs text-slate-600">Use a darker theme at night.</p>
          </div>
        </div>
        <Toggle checked={darkMode} onToggle={(v) => darkMode = v} label="" />
      </div>

      <!-- Notifications -->
      <div class="px-4 py-4 flex items-center justify-between border-b border-slate-100">
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
            <span class="text-lg">🔔</span>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-900">Notifications</p>
            <p class="text-xs text-slate-600">Get reminders for unpaid splits.</p>
          </div>
        </div>
        <Toggle checked={notifications} onToggle={(v) => notifications = v} label="" />
      </div>

      <!-- Sound Effects -->
      <div class="px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
            <span class="text-lg">🔊</span>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-900">Sound effects</p>
            <p class="text-xs text-slate-600">Play sounds on interactions.</p>
          </div>
        </div>
        <Toggle checked={soundEffects} onToggle={(v) => soundEffects = v} label="" />
      </div>
    </Card>
  </section>

  <!-- Social Section -->
  <section aria-label="Social" class="px-4 mt-6">
    <div class="flex items-center justify-between mb-2">
      <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Social</h2>
      <span class="text-xs text-slate-500">Groups & payments</span>
    </div>

    <Card padding="none">
      <!-- Manage Groups -->
      <button
        type="button"
        class="w-full px-4 py-4 flex items-center justify-between active:bg-slate-50 transition-colors"
        onclick={() => goto('/history#groups')}
      >
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <span class="text-lg">👥</span>
          </div>
          <div class="text-left">
            <p class="text-sm font-semibold text-slate-900">Manage groups</p>
            <p class="text-xs text-slate-600">Edit members and roles.</p>
          </div>
        </div>
        <span class="text-2xl text-slate-400" aria-hidden="true">→</span>
      </button>

      <div class="h-px bg-slate-100 mx-4"></div>

      <!-- Payment Methods -->
      <button
        type="button"
        class="w-full px-4 py-4 flex items-center justify-between active:bg-slate-50 transition-colors"
        onclick={() => alert('Payment methods coming soon')}
      >
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <span class="text-lg">💳</span>
          </div>
          <div class="text-left">
            <p class="text-sm font-semibold text-slate-900">Payment methods</p>
            <p class="text-xs text-slate-600">Linked cards and wallets.</p>
          </div>
        </div>
        <span class="text-2xl text-slate-400" aria-hidden="true">→</span>
      </button>

      <div class="h-px bg-slate-100 mx-4"></div>

      <!-- Sharing Preferences -->
      <button
        type="button"
        class="w-full px-4 py-4 flex items-center justify-between active:bg-slate-50 transition-colors"
        onclick={() => alert('Sharing preferences coming soon')}
      >
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <span class="text-lg">📤</span>
          </div>
          <div class="text-left">
            <p class="text-sm font-semibold text-slate-900">Sharing preferences</p>
            <p class="text-xs text-slate-600">Default invite settings.</p>
          </div>
        </div>
        <span class="text-2xl text-slate-400" aria-hidden="true">→</span>
      </button>
    </Card>
  </section>

  <!-- Data Section -->
  <section aria-label="Data" class="px-4 mt-6">
    <div class="flex items-center justify-between mb-2">
      <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Data</h2>
      <span class="text-xs text-slate-500">Export & insights</span>
    </div>

    <Card padding="none">
      <!-- Monthly Summary -->
      <button
        type="button"
        class="w-full px-4 py-4 flex items-center justify-between active:bg-slate-50 transition-colors"
        onclick={() => goto('/history#analytics')}
      >
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <span class="text-lg">📅</span>
          </div>
          <div class="text-left">
            <p class="text-sm font-semibold text-slate-900">Monthly summary</p>
            <p class="text-xs text-slate-600">Spending breakdown.</p>
          </div>
        </div>
        <span class="text-2xl text-slate-400" aria-hidden="true">→</span>
      </button>

      <div class="h-px bg-slate-100 mx-4"></div>

      <!-- Analytics -->
      <button
        type="button"
        class="w-full px-4 py-4 flex items-center justify-between active:bg-slate-50 transition-colors"
        onclick={() => goto('/history#analytics')}
      >
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <span class="text-lg">📊</span>
          </div>
          <div class="text-left">
            <p class="text-sm font-semibold text-slate-900">Analytics</p>
            <p class="text-xs text-slate-600">Visual charts & trends.</p>
          </div>
        </div>
        <span class="text-2xl text-slate-400" aria-hidden="true">→</span>
      </button>

      <div class="h-px bg-slate-100 mx-4"></div>

      <!-- Export CSV -->
      <div class="px-4 py-4">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3 min-w-0">
            <div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
              <span class="text-lg">📥</span>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold">Export CSV</p>
              <p class="text-xs text-slate-600">Download your split history.</p>
            </div>
          </div>
          <Button variant="outline" onclick={handleExportCSV}>Export</Button>
        </div>
      </div>

      <div class="h-px bg-slate-100 mx-4"></div>

      <!-- Clear Cache -->
      <div class="px-4 py-4">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3 min-w-0">
            <div class="h-11 w-11 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <span class="text-lg">🗑️</span>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold">Clear cache</p>
              <p class="text-xs text-slate-600">Frees space (keeps splits).</p>
            </div>
          </div>
          <Button variant="outline" onclick={handleClearCache}>Clear</Button>
        </div>
      </div>
    </Card>
  </section>

  <!-- Account Section -->
  <section aria-label="Account" class="px-4 mt-6">
    <div class="flex items-center justify-between mb-2">
      <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider">Account</h2>
      <span class="text-xs text-slate-500">Access & Privacy</span>
    </div>

    <Card padding="none">
      <!-- Privacy Settings -->
      <button
        type="button"
        class="w-full px-4 py-4 flex items-center justify-between active:bg-slate-50 transition-colors"
        onclick={() => alert('Privacy settings coming soon')}
      >
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-slate-100 text-slate-600 flex items-center justify-center">
            <span class="text-lg">🔒</span>
          </div>
          <div class="text-left">
            <p class="text-sm font-semibold text-slate-900">Privacy settings</p>
            <p class="text-xs text-slate-600">Manage data visibility.</p>
          </div>
        </div>
        <span class="text-2xl text-slate-400" aria-hidden="true">→</span>
      </button>

      <div class="h-px bg-slate-100 mx-4"></div>

      <!-- API Key -->
      <div class="px-4 py-4">
        <div class="flex items-center gap-3 mb-3">
          <div class="h-11 w-11 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center">
            <span class="text-lg">🔑</span>
          </div>
          <div>
            <p class="text-sm font-semibold">API key</p>
            <p class="text-xs text-slate-600">Used for receipt scanning integrations.</p>
          </div>
        </div>

        <div class="mt-3">
          <p class="text-xs font-semibold text-slate-600 mb-2">Key</p>
          <div class="flex items-stretch gap-2">
            <input
              type="text"
              readonly
              value="sb_live_24x9••••••••••••••••••••R7"
              class="h-11 flex-1 rounded-2xl bg-slate-50 px-3 text-sm text-slate-700 border border-slate-200 focus:outline-none"
            />
            <Button
              variant="outline"
              onclick={copyAPIKey}
              aria-label="Copy API key"
            >
              Copy
            </Button>
          </div>
        </div>
      </div>

      <div class="h-px bg-slate-100 mx-4"></div>

      <!-- App Version -->
      <div class="px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="h-11 w-11 rounded-2xl bg-slate-50 text-slate-400 flex items-center justify-center">
            <span class="text-lg">ℹ️</span>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-900">App version</p>
            <p class="text-xs text-slate-600">Build 2023.10.42</p>
          </div>
        </div>
        <span class="text-xs font-medium text-slate-400 bg-slate-100 px-2 py-1 rounded-lg">v2.4.0</span>
      </div>
    </Card>
  </section>

  <!-- Privacy Footer Note -->
  <div class="px-4 mt-6">
    <div class="bg-sky-50 border border-sky-100 px-4 py-3 rounded-3xl">
      <div class="flex items-start gap-3">
        <div class="mt-0.5 h-8 w-8 rounded-2xl bg-sky-500 text-white flex items-center justify-center shadow-md">
          <span class="text-lg">🛡️</span>
        </div>
        <div>
          <p class="text-sm font-semibold text-slate-900">Privacy-first</p>
          <p class="text-xs text-slate-600">Your splits stay on your device unless you share them.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Save Button -->
  <div class="px-4 pb-8 pt-4">
    <Button
      variant="primary"
      onclick={handleSaveSettings}
      class="w-full"
    >
      Save Settings
    </Button>
  </div>
</div>
