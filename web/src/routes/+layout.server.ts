import { initApiClient } from '$lib/services/api';
import type { RequestEvent } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export const load = async ({ url }: RequestEvent) => {
  // Initialize API client from environment variables
  const apiConfig = {
    baseURL: env.FASTAPI_API_URL || 'http://localhost:18000',
    apiKey: env.API_KEY || '',
    timeout: 30000,
  };

  initApiClient(apiConfig);

  return {};
};
