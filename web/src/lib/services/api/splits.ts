import { getApiClient } from './client';
import type {
  CalculateSplitRequest,
  CalculateSplitResponse,
  SharedSplitDataResponse
} from '$lib/types/api';

/** Split calculation service */
export class SplitsService {
  /** Calculate bill split */
  async calculate(request: CalculateSplitRequest): Promise<CalculateSplitResponse> {
    const apiClient = getApiClient();
    return apiClient.post<CalculateSplitResponse>('/splits/calculate', request);
  }

  /** Get shared split data */
  async getShared(splitId: string): Promise<SharedSplitDataResponse> {
    const apiClient = getApiClient();
    return apiClient.get<SharedSplitDataResponse>(`/splits/view/${splitId}`);
  }

  /** Owner only: mark one person on the split as paid or unpaid */
  async setPaid(splitId: string, personName: string, paid: boolean): Promise<unknown> {
    const apiClient = getApiClient();
    return apiClient.put(`/splits/${splitId}/payments/${encodeURIComponent(personName)}`, { paid });
  }
}

export const splitsService = new SplitsService();
