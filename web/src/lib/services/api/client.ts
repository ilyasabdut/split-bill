import type {
  ApiResponse,
  ApiError as ApiErrorType,
  UploadReceiptResponse,
  CalculateSplitRequest,
  CalculateSplitResponse,
  SharedSplitDataResponse,
  HealthResponse
} from '$lib/types/api';

export interface ApiConfig {
  baseURL: string;
  apiKey: string;
  timeout: number;
}

/** Custom API error class */
export class ApiError extends Error {
  constructor(
    public message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Type-safe API client */
export class ApiClient {
  private config: ApiConfig;

  constructor(config: ApiConfig) {
    this.config = config;
  }

  /** Make authenticated API request */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.config.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`,
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new ApiError(
          error.error?.detail || 'Request failed',
          response.status,
          error
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408);
      }
      throw new ApiError('Network error', 0);
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async postForm<T>(endpoint: string, formData: FormData): Promise<T> {
    const url = `${this.config.baseURL}${endpoint}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        error.error?.detail || 'Upload failed',
        response.status,
        error
      );
    }

    return response.json();
  }
}

/** Singleton instance */
let apiClientInstance: ApiClient | null = null;

/** Initialize API client with configuration */
export function initApiClient(config: ApiConfig): ApiClient {
  apiClientInstance = new ApiClient(config);
  return apiClientInstance;
}

/** Get initialized API client */
export function getApiClient(): ApiClient {
  if (!apiClientInstance) {
    throw new Error('API client not initialized. Call initApiClient first.');
  }
  return apiClientInstance;
}
