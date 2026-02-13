import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { analyticsStore } from '../analytics';

describe('analyticsStore', () => {
  beforeEach(() => {
    analyticsStore.reset();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = get(analyticsStore);
      expect(state).toEqual({
        spending: [],
        trends: null,
        loading: false,
        error: null
      });
    });
  });

  describe('setSpending', () => {
    it('should set spending data', () => {
      const spendingData = [
        { month: '2024-01', total: 1000000, currency: 'IDR' },
        { month: '2024-02', total: 1500000, currency: 'IDR' }
      ];

      analyticsStore.setSpending(spendingData);

      const state = get(analyticsStore);
      expect(state.spending).toEqual(spendingData);
      expect(state.loading).toBe(false);
    });
  });

  describe('setTrends', () => {
    it('should set trends data', () => {
      const trendsData = {
        months: [
          { month: '2024-01', total: 1000000, currency: 'IDR' },
          { month: '2024-02', total: 1500000, currency: 'IDR' }
        ],
        current_month_total: 1500000,
        previous_month_total: 1000000
      };

      analyticsStore.setTrends(trendsData);

      const state = get(analyticsStore);
      expect(state.trends).toEqual(trendsData);
      expect(state.loading).toBe(false);
    });
  });

  describe('setLoading', () => {
    it('should set loading state', () => {
      analyticsStore.setLoading(true);
      expect(get(analyticsStore).loading).toBe(true);

      analyticsStore.setLoading(false);
      expect(get(analyticsStore).loading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should set error message', () => {
      const errorMessage = 'Failed to load analytics';
      analyticsStore.setError(errorMessage);

      const state = get(analyticsStore);
      expect(state.error).toBe(errorMessage);
      expect(state.loading).toBe(false);
    });

    it('should clear error when null is passed', () => {
      analyticsStore.setError('Some error');
      expect(get(analyticsStore).error).toBe('Some error');

      analyticsStore.setError(null);
      expect(get(analyticsStore).error).toBeNull();
    });
  });

  describe('selectors', () => {
    it('should select spending data', () => {
      const spendingData = [{ month: '2024-01', total: 1000000, currency: 'IDR' }];
      analyticsStore.setSpending(spendingData);

      const spending = get(analyticsStore.spending);
      expect(spending).toEqual(spendingData);
    });

    it('should select trends data', () => {
      const trendsData = {
        months: [],
        current_month_total: 0,
        previous_month_total: 0
      };
      analyticsStore.setTrends(trendsData);

      const trends = get(analyticsStore.trends);
      expect(trends).toEqual(trendsData);
    });

    it('should select loading state', () => {
      analyticsStore.setLoading(true);
      const loading = get(analyticsStore.isLoading);
      expect(loading).toBe(true);
    });

    it('should select error', () => {
      analyticsStore.setError('Test error');
      const error = get(analyticsStore.error);
      expect(error).toBe('Test error');
    });
  });

  describe('reset', () => {
    it('should reset to initial state', () => {
      // Set some state
      analyticsStore.setSpending([{ month: '2024-01', total: 1000000, currency: 'IDR' }]);
      analyticsStore.setLoading(true);
      analyticsStore.setError('Test error');

      // Reset
      analyticsStore.reset();

      const state = get(analyticsStore);
      expect(state).toEqual({
        spending: [],
        trends: null,
        loading: false,
        error: null
      });
    });
  });
});
