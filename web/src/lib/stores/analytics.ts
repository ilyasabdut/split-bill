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

    reset: () => set(initialState),

    /** Load analytics data from API */
    async loadAnalytics() {
      update(s => ({ ...s, loading: true }));
      try {
        const response = await fetch('/api/analytics/splits?range=month');
        if (!response.ok) throw new Error('Failed to load analytics');

        const data = await response.json();
        update(s => ({
          ...s,
          spending: data.spending || [],
          trends: data.trends || null,
          loading: false
        }));
      } catch (err) {
        const error = err instanceof Error ? err.message : 'Unknown error';
        update(s => ({ ...s, error, loading: false }));
      }
    },

    /** Get spending insights (derived from spending data) */
    getSpendingInsights() {
      const spending = this.spending?.();
      return spending.length > 0 ? {
        thisMonth: spending[0]?.total || 0,
        avgSplit: 0,
        totalSplits: spending.length
      } : null;
    },

    /** Get monthly spending data */
    getMonthlySpending(): Record<string, number> {
      const spending = this.spending?.();
      return spending.reduce((acc: Record<string, number>, item) => {
        acc[item.month] = item.total;
        return acc;
      }, {});
    },

    /** Get settlement summary */
    getSettlementSummary(): Record<string, any> {
      return {
        totalOwed: 0,
        totalReceives: 0,
        settlements: {}
      };
    },

    /** Export analytics data */
    async exportData(format: 'csv' | 'json') {
      const spending = this.spending?.();
      const trends = this.trends?.();

      const data = {
        spending: spending,
        trends: trends,
        exportedAt: new Date().toISOString()
      };

      if (format === 'json') {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
      } else if (format === 'csv') {
        const csvContent = 'Month,Total\n' + spending.map(s => `${s.month},${s.total}`).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      }
    },
  }
}

export const analyticsStore = createAnalyticsStore();
