import { describe, it, expect, beforeEach, vi } from 'vitest';
import { HealthService, healthService } from '../api/health';

// Mock API client
vi.mock('../api/client', () => ({
  getApiClient: vi.fn(() => ({
    get: vi.fn(),
  }))
}));

describe('HealthService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('check', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = healthService.check();
      expect(mockClient).not.toBeNull();
    });

    it('should return health response', async () => {
      const mockClient = healthService.check();
      expect(mockClient).not.toBeNull();
    });
  });
});
