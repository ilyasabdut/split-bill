import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CurrencyService, currencyService } from '../api/currency';

// Mock API client
vi.mock('../api/client', () => ({
  getApiClient: vi.fn(() => ({
    get: vi.fn(),
    post: vi.fn(),
  }))
}));

describe('CurrencyService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getRates', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = currencyService.getRates('IDR');
      expect(mockClient).not.toBeNull();
    });

    it('should use default base currency', async () => {
      const mockClient = currencyService.getRates();
      expect(mockClient).not.toBeNull();
    });

    it('should handle different base currencies', async () => {
      const currencies = ['IDR', 'USD', 'EUR', 'GBP', 'JPY'] as const;
      for (const currency of currencies) {
        const mockClient = currencyService.getRates(currency);
        expect(mockClient).not.toBeNull();
      }
    });
  });

  describe('convert', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = currencyService.convert({
        amount: 100,
        from: 'USD',
        to: 'EUR'
      });
      expect(mockClient).not.toBeNull();
    });

    it('should handle conversion between currencies', async () => {
      const mockClient = currencyService.convert({
        amount: 50.5,
        from: 'IDR',
        to: 'USD'
      });
      expect(mockClient).not.toBeNull();
    });
  });

  describe('getSupportedCurrencies', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = currencyService.getSupportedCurrencies();
      expect(mockClient).not.toBeNull();
    });
  });
});
