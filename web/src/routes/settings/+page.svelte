<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import CurrencySelector from '$lib/components/CurrencySelector.svelte';
  import { offlineStore, currencyStore, groupsStore, templatesStore, analyticsStore } from '$lib/stores';
  import { getIndexedDB, STORES } from '$lib/services/offline/indexeddb';

  let clearingCache = $state(false);
  let cacheSize = $state(0);
  let darkMode = $state(false);
  let analyticsEnabled = $state(true);
  let notificationsEnabled = $state(true);
  let selectedCurrency = $state('USD');

  onMount(async () => {
    await Promise.all([
      currencyStore.init(),
      groupsStore.loadGroups(),
      templatesStore.loadTemplates()
    ]);

    // Load preferences
    const savedPreferences = localStorage.getItem('split-bill-preferences');
    if (savedPreferences) {
      const prefs = JSON.parse(savedPreferences);
      darkMode = prefs.darkMode || false;
      analyticsEnabled = prefs.analyticsEnabled !== false;
      notificationsEnabled = prefs.notificationsEnabled !== false;
      selectedCurrency = prefs.currency || 'USD';
    }

    calculateCacheSize();
  });

  // Calculate cache size on mount
  async function calculateCacheSize() {
    try {
      const indexedDB = await getIndexedDB();
      const splits = await indexedDB.getAll(STORES.SPLITS);
      const receipts = await indexedDB.getAll(STORES.RECEIPTS);

      // Rough estimation (actual size would need more complex calculation)
      cacheSize = splits.length + receipts.length;
    } catch (error) {
      console.error('Failed to calculate cache size:', error);
    }
  }

  function savePreferences() {
    const prefs = {
      darkMode,
      analyticsEnabled,
      notificationsEnabled,
      currency: selectedCurrency
    };
    localStorage.setItem('split-bill-preferences', JSON.stringify(prefs));

    // Apply dark mode
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    alert('Preferences saved!');
  }

  async function clearCache() {
    if (!confirm('This will clear all cached data. Are you sure?')) return;

    clearingCache = true;
    try {
      const indexedDB = await getIndexedDB();
      await indexedDB.clear(STORES.SPLITS);
      await indexedDB.clear(STORES.RECEIPTS);
      await indexedDB.clear(STORES.OFFLINE_QUEUE);

      cacheSize = 0;
      offlineStore.resetQueued();

      alert('Cache cleared successfully!');
    } catch (error) {
      console.error('Failed to clear cache:', error);
      alert('Failed to clear cache');
    } finally {
      clearingCache = false;
    }
  }

  async function exportData() {
    try {
      const data = await analyticsStore.exportAllData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `split-bill-backup-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert('Failed to export data');
    }
  }

  function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      try {
        const text = await file.text();
        const data = JSON.parse(text);
        await analyticsStore.importData(data);
        alert('Data imported successfully!');
        window.location.reload();
      } catch (error) {
        alert('Failed to import data');
      }
    };
    input.click();
  }
</script>

<svelte:head>
  <title>Settings - Split Bill</title>
</svelte:head>

<div class="space-y-4">
  <h2 class="text-xl font-semibold">Settings</h2>

  <!-- Data Management -->
  <Card>
    <div class="space-y-4">
      <h3 class="font-semibold">Data Management</h3>

      <div class="space-y-3">
        <div class="flex justify-between items-center">
          <div>
            <p class="font-medium">Cached Data</p>
            <p class="text-sm text-text-secondary">{cacheSize} items stored offline</p>
          </div>
          <Button
            variant="secondary"
            onclick={calculateCacheSize}
            disabled={clearingCache}
          >
            Refresh
          </Button>
        </div>

        <div class="flex gap-2">
          <Button
            variant="danger"
            onclick={clearCache}
            disabled={clearingCache}
            class="flex-1"
          >
            {clearingCache ? 'Clearing...' : 'Clear Cache'}
          </Button>
        </div>
      </div>
    </div>
  </Card>

  <!-- Import/Export -->
  <Card>
    <div class="space-y-4">
      <h3 class="font-semibold">Backup & Restore</h3>

      <div class="space-y-3">
        <Button
          variant="secondary"
          onclick={exportData}
          class="w-full"
        >
          📤 Export Data
        </Button>

        <Button
          variant="secondary"
          onclick={importData}
          class="w-full"
        >
          📥 Import Data
        </Button>
      </div>
    </div>
  </Card>

  <!-- About -->
  <Card>
    <div class="space-y-2">
      <h3 class="font-semibold">About</h3>
      <p class="text-sm text-text-secondary">
        Split Bill v1.0.0
      </p>
      <p class="text-sm text-text-secondary">
        A progressive web app for splitting bills with friends.
      </p>
    </div>
  </Card>
</div>
