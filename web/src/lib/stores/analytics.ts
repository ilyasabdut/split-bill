import { writable, derived } from 'svelte/store';

export interface SpendingData {
  month: string;
  total: number;
  currency: string;
}

export interface SpendingTrends {
  months: SpendingData[];
  current_month_total: number;
  previous_month_total: number;
}

interface AnalyticsState {
  spending: SpendingData[];
  trends: SpendingTrends | null;
  loading: boolean;
  error: string | null;
}

const initialState: AnalyticsState = {
  spending: [],
  trends: null,
  loading: false,
  error: null
};

function createAnalyticsStore() {
  const { subscribe, update, set } = writable(initialState);

  return {
    subscribe,

    spending: derived({ subscribe }, $s => $s.spending),
    trends: derived({ subscribe }, $s => $s.trends),
    isLoading: derived({ subscribe }, $s => $s.loading),
    error: derived({ subscribe }, $s => $s.error),

    setSpending: (spending: SpendingData[]) => update(s => ({ ...s, spending, loading: false })),

    setTrends: (trends: SpendingTrends) => update(s => ({ ...s, trends, loading: false })),

    setLoading: (loading: boolean) => update(s => ({ ...s, loading })),

    setError: (error: string | null) => update(s => ({ ...s, error, loading: false })),

    reset: () => set(initialState)
  };
}

export const analyticsStore = createAnalyticsStore();
