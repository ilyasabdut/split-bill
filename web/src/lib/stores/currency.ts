import { writable, derived } from 'svelte/store';

export type CurrencyCode = 'IDR' | 'USD' | 'EUR' | 'GBP' | 'JPY' | 'NZD';

interface CurrencyState {
  selected: CurrencyCode;
  baseCurrency: CurrencyCode;
  targetCurrency: CurrencyCode;
  exchangeRate: number;
  rates: Record<string, number>;
  loading: boolean;
  error: string | null;
}

const initialState: CurrencyState = {
  selected: 'IDR',
  baseCurrency: 'USD',
  targetCurrency: 'IDR',
  exchangeRate: 1,
  rates: {},
  loading: false,
  error: null
};

function createCurrencyStore() {
  const { subscribe, update, set } = writable(initialState);

  return {
    subscribe,

    selected: derived({ subscribe }, $s => $s.selected),
    baseCurrency: derived({ subscribe }, $s => $s.baseCurrency),
    targetCurrency: derived({ subscribe }, $s => $s.targetCurrency),
    exchangeRate: derived({ subscribe }, $s => $s.exchangeRate),
    rates: derived({ subscribe }, $s => $s.rates),
    isLoading: derived({ subscribe }, $s => $s.loading),
    error: derived({ subscribe }, $s => $s.error),
    hasRates: derived({ subscribe }, $s => Object.keys($s.rates).length > 0),
    availableCurrencies: derived({ subscribe }, $s => Object.keys($s.rates)),
    currencyPair: derived({ subscribe }, $s => `${$s.baseCurrency}/${$s.targetCurrency}`),

    setCurrency: (code: CurrencyCode) => update(s => ({ ...s, selected: code })),
    setBaseCurrency: (code: CurrencyCode) => update(s => ({ ...s, baseCurrency: code })),
    setTargetCurrency: (code: CurrencyCode) => update(s => ({ ...s, targetCurrency: code })),
    setExchangeRate: (rate: number) => update(s => ({ ...s, exchangeRate: rate })),

    setRates: (rates: Record<string, number>) => update(s => ({
      ...s,
      rates: { ...rates },
      loading: false
    })),

    setLoading: (loading: boolean) => update(s => ({ ...s, loading })),

    setError: (error: string | null) => update(s => ({ ...s, error, loading: false })),

    swapCurrencies: () => update(s => ({
      ...s,
      baseCurrency: s.targetCurrency,
      targetCurrency: s.baseCurrency,
      exchangeRate: 1 / s.exchangeRate
    })),

    getRateForCurrency: (code: CurrencyCode) => derived({ subscribe }, $s => $s.rates[code]),

    convert: (amount: number, from: CurrencyCode, to: CurrencyCode) => {
      return derived({ subscribe }, $s => {
        if (!amount || !$s.rates[from] || !$s.rates[to]) return 0;
        return (amount / $s.rates[from]) * $s.rates[to];
      });
    },

    convertAmount: (amount: number, reverse = false) => {
      return derived({ subscribe }, $s => {
        if (!amount || !$s.exchangeRate) return 0;
        return reverse ? amount / $s.exchangeRate : amount * $s.exchangeRate;
      });
    },

    convertBaseToTarget: (amount: number) => {
      return derived({ subscribe }, $s => {
        if (!amount || !$s.exchangeRate) return 0;
        return amount * $s.exchangeRate;
      });
    },

    convertTargetToBase: (amount: number) => {
      return derived({ subscribe }, $s => {
        if (!amount || !$s.exchangeRate) return 0;
        return amount / $s.exchangeRate;
      });
    },

    /** Reset store to initial state */
    reset: () => set(initialState),

     /** Initialize currency store - load rates from API */
    async init() {
      update(s => ({ ...s, loading: true }));
      try {
        const response = await fetch('/api/currency/rates');
        if (!response.ok) throw new Error('Failed to load currency rates');

        const data = await response.json();
        update(s => ({
          ...s,
          rates: data.rates || {},
          loading: false
        }));
      } catch (err) {
        const error = err instanceof Error ? err.message : 'Unknown error';
        update(s => ({ ...s, error, loading: false }));
      }
    },

    /** Format currency amount with proper symbol */
    formatCurrency: (amount: number, currencyCode?: CurrencyCode) => {
      return derived({ subscribe }, $s => {
        const code = currencyCode || $s.selected;
        const symbols: Record<CurrencyCode, string> = {
          'IDR': 'Rp',
          'USD': '$',
          'EUR': '€',
          'GBP': '£',
          'JPY': '¥',
          'NZD': '$'
        };

        const symbol = symbols[code];

        // Handle unknown currencies
        if (!symbol) {
          return `${amount} XXX`;
        }

        // JPY and IDR should not show decimal places
        const hasDecimals = code !== 'JPY' && code !== 'IDR';
        const formatter = new Intl.NumberFormat('en-US', {
          minimumFractionDigits: hasDecimals ? 2 : 0,
          maximumFractionDigits: hasDecimals ? 2 : 0
        });

        if (amount < 0) {
          return `-${symbol}${formatter.format(Math.abs(amount))}`;
        }

        return `${symbol}${formatter.format(amount)}`;
      });
    },
  }
}

export const currencyStore = createCurrencyStore();
