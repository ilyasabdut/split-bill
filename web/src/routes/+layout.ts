import { initApiClient } from '$lib/services/api';
import type { LayoutLoad } from './$types';

export const ssr = false;

export const load: LayoutLoad = async () => {
  const apiConfig = {
    baseURL: import.meta.env.VITE_FASTAPI_API_URL || '/api',
    apiKey: import.meta.env.VITE_API_KEY || '',
    timeout: 30000,
  };

  initApiClient(apiConfig);

  return {};
};
