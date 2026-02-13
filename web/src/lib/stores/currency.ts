import { writable, derived } from 'svelte/store';

export type CurrencyCode = 'IDR' | 'USD' | 'NZD' | 'JPY';

interface CurrencyState {
  selected: CurrencyCode;
  rates: Record<string, number>;
  loading: boolean;
  error: string | null;
}

const initialState: CurrencyState = {
  selected: 'IDR',
  rates: {
    'IDR': 1,
    'USD': 0.000064, // Approximate default
    'NZD': 0.00010,
    'JPY': 0.0096
  },
  loading: false,
  error: null
};

function createCurrencyStore() {
  const { subscribe, update, set } = writable(initialState);

  return {
    subscribe,

    selected: derived({ subscribe }, $s => $s.selected),
    rates: derived({ subscribe }, $s => $s.rates),
    isLoading: derived({ subscribe }, $s => $s.loading),
    error: derived({ subscribe }, $s => $s.error),

    setCurrency: (code: CurrencyCode) => update(s => ({ ...s, selected: code })),

    setRates: (rates: Record<string, number>) => update(s => ({
      ...s,
      rates: { ...s.rates, ...rates },
      loading: false
    })),

    setLoading: (loading: boolean) => update(s => ({ ...s, loading })),

    setError: (error: string | null) => update(s => ({ ...s, error, loading: false })),

    convert: (amount: number, from: string, to: string) => {
      // Logic would need access to current rates, but stores are reactive.
      // Ideally this is a utility function that takes rates as arg,
      // or we expose a helper that subscribes briefly.
      // For now, let's keep it simple and assume components handle conversion using $rates
      return 0;
    }
  };
}

export const currencyStore = createCurrencyStore();
