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
}

export const splitsService = new SplitsService();
