import { describe, it, expect, vi, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { currencyStore } from './currency';

// Mock the API service
vi.mock('$lib/services/api/currency', () => ({
  currencyService: {
    getRates: vi.fn(),
    convert: vi.fn()
  }
}));

describe('Currency Store', () => {
  beforeEach(() => {
    // Reset store
    currencyStore.reset();
    vi.clearAllMocks();
  });

  describe('initialization', () => {
    it('should initialize with default values', () => {
      expect(get(currencyStore.baseCurrency)).toBe('USD');
      expect(get(currencyStore.targetCurrency)).toBe('IDR');
      expect(get(currencyStore.exchangeRate)).toBe(1);
      expect(get(currencyStore.rates)).toEqual({});
      expect(get(currencyStore.isLoading)).toBe(false);
      expect(get(currencyStore.error)).toBe(null);
    });
  });

  describe('currency selection', () => {
    it('should set base currency', () => {
      currencyStore.setBaseCurrency('EUR');
      expect(get(currencyStore.baseCurrency)).toBe('EUR');
    });

    it('should set target currency', () => {
      currencyStore.setTargetCurrency('GBP');
      expect(get(currencyStore.targetCurrency)).toBe('GBP');
    });

    it('should swap currencies', () => {
      currencyStore.setBaseCurrency('USD');
      currencyStore.setTargetCurrency('EUR');

      currencyStore.swapCurrencies();

      expect(get(currencyStore.baseCurrency)).toBe('EUR');
      expect(get(currencyStore.targetCurrency)).toBe('USD');
    });
  });

  describe('rate management', () => {
    it('should set exchange rate', () => {
      currencyStore.setExchangeRate(0.85);
      expect(get(currencyStore.exchangeRate)).toBe(0.85);
    });

    it('should set rates', () => {
      const rates = {
        EUR: 0.85,
        GBP: 0.73,
        JPY: 110.0
      };

      currencyStore.setRates(rates);
      expect(get(currencyStore.rates)).toEqual(rates);
    });

    it('should get rate for currency', () => {
      const rates = {
        EUR: 0.85,
        GBP: 0.73,
        JPY: 110.0
      };

      currencyStore.setRates(rates);

      expect(get(currencyStore.getRateForCurrency('EUR'))).toBe(0.85);
      expect(get(currencyStore.getRateForCurrency('GBP'))).toBe(0.73);
      expect(get(currencyStore.getRateForCurrency('JPY'))).toBe(110.0);
      expect(get(currencyStore.getRateForCurrency('CAD'))).toBeUndefined();
    });
  });

  describe('loading and error states', () => {
    it('should set loading state', () => {
      currencyStore.setLoading(true);
      expect(get(currencyStore.isLoading)).toBe(true);

      currencyStore.setLoading(false);
      expect(get(currencyStore.isLoading)).toBe(false);
    });

    it('should set error state', () => {
      currencyStore.setError('Failed to fetch rates');
      expect(get(currencyStore.error)).toBe('Failed to fetch rates');
    });

    it('should clear error state', () => {
      currencyStore.setError('Some error');
      expect(get(currencyStore.error)).toBe('Some error');

      currencyStore.setError(null);
      expect(get(currencyStore.error)).toBe(null);
    });
  });

  describe('conversion', () => {
    beforeEach(() => {
      currencyStore.setExchangeRate(0.85);
    });

    it('should convert amount from base to target currency', () => {
      currencyStore.setBaseCurrency('USD');
      currencyStore.setTargetCurrency('EUR');

      const converted = get(currencyStore.convertAmount(100));
      expect(converted).toBe(85);
    });

    it('should convert amount from target to base currency', () => {
      currencyStore.setBaseCurrency('USD');
      currencyStore.setTargetCurrency('EUR');

      const converted = get(currencyStore.convertAmount(85, true));
      expect(converted).toBe(100);
    });

    it('should handle zero amounts', () => {
      const converted = get(currencyStore.convertAmount(0));
      expect(converted).toBe(0);
    });

    it('should handle negative amounts', () => {
      const converted = get(currencyStore.convertAmount(-100));
      expect(converted).toBe(-85);
    });

    it('should handle decimal amounts', () => {
      const converted = get(currencyStore.convertAmount(123.45));
      expect(converted).toBeCloseTo(104.93, 2);
    });
  });

  describe('formatting', () => {
    it('should format currency amount', () => {
      expect(get(currencyStore.formatCurrency(100, 'USD'))).toBe('$100.00');
      expect(get(currencyStore.formatCurrency(100, 'EUR'))).toBe('€100.00');
      expect(get(currencyStore.formatCurrency(100, 'GBP'))).toBe('£100.00');
      expect(get(currencyStore.formatCurrency(100, 'JPY'))).toBe('¥100');
      expect(get(currencyStore.formatCurrency(100, 'IDR'))).toBe('Rp100');
    });

    it('should format with different decimal places', () => {
      expect(get(currencyStore.formatCurrency(100.123, 'USD'))).toBe('$100.12');
      expect(get(currencyStore.formatCurrency(100.999, 'USD'))).toBe('$101.00');
    });

    it('should handle zero amounts', () => {
      expect(get(currencyStore.formatCurrency(0, 'USD'))).toBe('$0.00');
    });

    it('should handle negative amounts', () => {
      expect(get(currencyStore.formatCurrency(-50, 'USD'))).toBe('-$50.00');
    });

    it('should handle unknown currencies', () => {
      expect(get(currencyStore.formatCurrency(100, 'XXX'))).toBe('100 XXX');
    });
  });

  describe('reset functionality', () => {
    it('should reset all values to initial state', () => {
      // Set some values
      currencyStore.setBaseCurrency('EUR');
      currencyStore.setTargetCurrency('GBP');
      currencyStore.setExchangeRate(0.85);
      currencyStore.setRates({ EUR: 0.85, GBP: 0.73 });
      currencyStore.setLoading(true);
      currencyStore.setError('Error');

      // Verify values are set
      expect(get(currencyStore.baseCurrency)).toBe('EUR');
      expect(get(currencyStore.targetCurrency)).toBe('GBP');
      expect(get(currencyStore.exchangeRate)).toBe(0.85);
      expect(get(currencyStore.rates)).toEqual({ EUR: 0.85, GBP: 0.73 });
      expect(get(currencyStore.isLoading)).toBe(true);
      expect(get(currencyStore.error)).toBe('Error');

      // Reset
      currencyStore.reset();

      // Verify reset
      expect(get(currencyStore.baseCurrency)).toBe('USD');
      expect(get(currencyStore.targetCurrency)).toBe('IDR');
      expect(get(currencyStore.exchangeRate)).toBe(1);
      expect(get(currencyStore.rates)).toEqual({});
      expect(get(currencyStore.isLoading)).toBe(false);
      expect(get(currencyStore.error)).toBe(null);
    });
  });

  describe('derived stores', () => {
    it('should check if has rates', () => {
      expect(get(currencyStore.hasRates)).toBe(false);

      currencyStore.setRates({ EUR: 0.85 });
      expect(get(currencyStore.hasRates)).toBe(true);

      currencyStore.setRates({});
      expect(get(currencyStore.hasRates)).toBe(false);
    });

    it('should get available currencies', () => {
      expect(get(currencyStore.availableCurrencies)).toEqual([]);

      const rates = {
        EUR: 0.85,
        GBP: 0.73,
        JPY: 110.0
      };

      currencyStore.setRates(rates);
      const available = get(currencyStore.availableCurrencies);
      expect(available).toEqual(['EUR', 'GBP', 'JPY']);
      expect(available).toHaveLength(3);
    });

    it('should get currency pair', () => {
      currencyStore.setBaseCurrency('USD');
      currencyStore.setTargetCurrency('EUR');

      expect(get(currencyStore.currencyPair)).toBe('USD/EUR');

      currencyStore.setBaseCurrency('GBP');
      currencyStore.setTargetCurrency('JPY');

      expect(get(currencyStore.currencyPair)).toBe('GBP/JPY');
    });
  });
});
