<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { CurrencyCode } from '$lib/stores/currency';
  import { currencyStore } from '$lib/stores/currency';
  import { currencyService } from '$lib/services/api/currency';
  import { onMount } from 'svelte';

  interface Props {
    selected?: CurrencyCode;
    onChange?: (currency: CurrencyCode) => void;
    disabled?: boolean;
    class?: string;
    showSymbol?: boolean;
    children?: Snippet;
  }

  const {
    selected = $derived(currencyStore.selected),
    onChange,
    disabled = false,
    class: className = '',
    showSymbol = false,
    children
  }: Props = $props();

  let loading = $state(false);
  let error = $state('');
  let currencies = $state<Array<{
    code: CurrencyCode;
    name: string;
    symbol: string;
  }>>([]);

  onMount(async () => {
    try {
      loading = true;
      currencies = await currencyService.getSupportedCurrencies();
    } catch (err) {
      error = 'Failed to load currencies';
      console.error('Error loading currencies:', err);
    } finally {
      loading = false;
    }
  });

  async function handleChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newCurrency = target.value as CurrencyCode;

    currencyStore.setCurrency(newCurrency);
    onChange?.(newCurrency);
  }
</script>

<div class="relative {className}">
  {#if loading}
    <div class="animate-pulse bg-surface-200 rounded-lg h-10"></div>
  {:else if error}
    <div class="text-sm text-red-600">{error}</div>
  {:else}
    <select
      value={$selected}
      onchange={handleChange}
      {disabled}
      class="block w-full appearance-none bg-surface-100 border border-surface-300 rounded-lg px-4 py-2 pr-8 text-text focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
    >
      {#if children}
        {@render children()}
      {/if}
      {#each currencies as currency}
        <option value={currency.code}>
          {currency.code}
          {#if showSymbol}
            - {currency.symbol}
          {/if}
          - {currency.name}
        </option>
      {/each}
    </select>

    <!-- Dropdown arrow -->
    <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
      <svg class="w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
      </svg>
    </div>
  {/if}
</div>
