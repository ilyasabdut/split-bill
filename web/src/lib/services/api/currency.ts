import { getApiClient } from './client';
import type { CurrencyCode } from '$lib/stores/currency';

export interface ExchangeRatesResponse {
  base: string;
  rates: Record<string, number>;
  timestamp: number;
}

export interface ConvertCurrencyRequest {
  amount: number;
  from: CurrencyCode;
  to: CurrencyCode;
}

export interface ConvertCurrencyResponse {
  amount: number;
  converted_amount: number;
  from: CurrencyCode;
  to: CurrencyCode;
  rate: number;
}

/** Currency exchange service */
export class CurrencyService {
  /** Get current exchange rates */
  async getRates(baseCurrency: CurrencyCode = 'IDR'): Promise<ExchangeRatesResponse> {
    const apiClient = getApiClient();
    return apiClient.get<ExchangeRatesResponse>(`/currency/rates?base=${baseCurrency}`);
  }

  /** Convert amount between currencies */
  async convert(request: ConvertCurrencyRequest): Promise<ConvertCurrencyResponse> {
    const apiClient = getApiClient();
    return apiClient.post<ConvertCurrencyResponse>('/currency/convert', request);
  }

  /** Get supported currencies */
  async getSupportedCurrencies(): Promise<Array<{
    code: CurrencyCode;
    name: string;
    symbol: string;
  }>> {
    const apiClient = getApiClient();
    return apiClient.get('/currency/supported');
  }
}

export const currencyService = new CurrencyService();
