import { getApiClient } from './client';
import type { HealthResponse } from '$lib/types/api';

/** Health check service */
export class HealthService {
  /** Check API health */
  async check(): Promise<HealthResponse> {
    const apiClient = getApiClient();
    return apiClient.get<HealthResponse>('/health');
  }
}

export const healthService = new HealthService();
