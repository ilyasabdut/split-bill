import { initApiClient } from '$lib/services/api';
import type { RequestEvent } from '@sveltejs/kit';

export const load = async ({ url }: RequestEvent) => {
  // Initialize API client from environment variables
  const apiConfig = {
    baseURL: 'http://localhost:8000',
    apiKey: '',
    timeout: 30000,
  };

  initApiClient(apiConfig);

  return {};
};
