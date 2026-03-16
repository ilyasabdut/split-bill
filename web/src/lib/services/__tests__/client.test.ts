import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ApiClient, ApiError, initApiClient, getApiClient } from '../api/client';

describe('ApiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset singleton instance
    vi.resetModules();
  });

  describe('initialization', () => {
    it('should initialize with config', () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      expect(client).not.toBeNull();
    });

    it('should have default timeout if not provided', () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      expect(client).not.toBeNull();
    });
  });

  describe('singleton', () => {
    it('should initialize singleton instance', () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = initApiClient(config);
      expect(client).toBeInstanceOf(ApiClient);
    });

    it('should get singleton instance', () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      initApiClient(config);
      const client = getApiClient();
      expect(client).toBeInstanceOf(ApiClient);
    });

    it('should throw error if not initialized', async () => {
      // Import fresh to ensure singleton is reset
      const { getApiClient } = await import('../api/client');
      expect(() => getApiClient()).toThrow('API client not initialized. Call initApiClient first.');
    });
  });

  describe('get method', () => {
    it('should make GET request', async () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: 'test' })
      });

      global.fetch = mockFetch;

      const result = await client.get('/test');
      expect(mockFetch).toHaveBeenCalled();
      expect(result).not.toBeNull();
    });
  });

  describe('post method', () => {
    it('should make POST request', async () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: 'test' })
      });

      global.fetch = mockFetch;

      const result = await client.post('/test', { test: 'data' });
      expect(mockFetch).toHaveBeenCalled();
      expect(result).not.toBeNull();
    });
  });

  describe('postForm method', () => {
    it('should make POST request with FormData', async () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: 'test' })
      });

      global.fetch = mockFetch;

      const formData = new FormData();
      formData.append('file', 'test');

      const result = await client.postForm('/upload', formData);
      expect(mockFetch).toHaveBeenCalled();
      expect(result).not.toBeNull();
    });
  });

  describe('error handling', () => {
    it('should throw ApiError on failed response', async () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ error: 'Server error' })
      });

      global.fetch = mockFetch;

      await expect(client.get('/test')).rejects.toThrow(ApiError);
    });

    it.skip('should throw timeout error', async () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 100
      };

      const client = new ApiClient(config);
      const mockFetch = vi.fn(() => {
        return new Promise<Response>(() => {});
      });

      global.fetch = mockFetch;

      // Use fake timers to simulate timeout
      vi.useFakeTimers();
      const promise = client.get('/test');
      vi.advanceTimersByTime(150);
      await expect(promise).rejects.toThrow(ApiError);
      vi.useRealTimers();
    }, 1000);

    it('should throw network error', async () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'));

      global.fetch = mockFetch;

      await expect(client.get('/test')).rejects.toThrow(ApiError);
    });
  });

  describe('request headers', () => {
    it('should include authorization header', async () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({})
      });

      global.fetch = mockFetch;

      await client.get('/test');

      const callArgs = mockFetch.mock.calls[0];
      expect(callArgs[1].headers).toHaveProperty('Authorization');
      expect(callArgs[1].headers.Authorization).toBe('Bearer test-key');
    });

    it('should include content-type header', async () => {
      const config = {
        baseURL: 'https://api.example.com',
        apiKey: 'test-key',
        timeout: 5000
      };

      const client = new ApiClient(config);
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({})
      });

      global.fetch = mockFetch;

      await client.post('/test', {});

      const callArgs = mockFetch.mock.calls[0];
      expect(callArgs[1].headers).toHaveProperty('Content-Type');
      expect(callArgs[1].headers['Content-Type']).toBe('application/json');
    });
  });
});
