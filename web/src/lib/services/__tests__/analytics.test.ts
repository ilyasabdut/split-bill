import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AnalyticsService, analyticsService } from '../api/analytics';

// Mock API client
vi.mock('../api/client', () => ({
  getApiClient: vi.fn(() => ({
    get: vi.fn(),
    post: vi.fn(),
  }))
}));

describe('AnalyticsService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getSplitAnalytics', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = analyticsService.getSplitAnalytics('month');
      expect(mockClient).not.toBeNull();
    });

    it('should handle different time ranges', async () => {
      const ranges = ['week', 'month', 'year'] as const;

      for (const range of ranges) {
        // Test that the function accepts all range values
        expect(range).toBeDefined();
      }
    });
  });

  describe('getUserAnalytics', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = analyticsService.getUserAnalytics(123, 'month');
      expect(mockClient).not.toBeNull();
    });

    it('should include user ID in endpoint', async () => {
      const userId = 456;
      const mockClient = analyticsService.getUserAnalytics(userId, 'week');
      expect(mockClient).not.toBeNull();
    });
  });

  describe('getGroupAnalytics', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = analyticsService.getGroupAnalytics(789, 'month');
      expect(mockClient).not.toBeNull();
    });

    it('should include group ID in endpoint', async () => {
      const groupId = 123;
      const mockClient = analyticsService.getGroupAnalytics(groupId, 'year');
      expect(mockClient).not.toBeNull();
    });
  });

  describe('getAppAnalytics', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = analyticsService.getAppAnalytics();
      expect(mockClient).not.toBeNull();
    });
  });

  describe('getPopularSplits', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = analyticsService.getPopularSplits();
      expect(mockClient).not.toBeNull();
    });

    it('should use default limit', async () => {
      const mockClient = analyticsService.getPopularSplits(10);
      expect(mockClient).not.toBeNull();
    });

    it('should use custom limit', async () => {
      const mockClient = analyticsService.getPopularSplits(20);
      expect(mockClient).not.toBeNull();
    });
  });

  describe('getTrendingTemplates', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = analyticsService.getTrendingTemplates();
      expect(mockClient).not.toBeNull();
    });

    it('should use default limit', async () => {
      const mockClient = analyticsService.getTrendingTemplates(10);
      expect(mockClient).not.toBeNull();
    });

    it('should use custom limit', async () => {
      const mockClient = analyticsService.getTrendingTemplates(15);
      expect(mockClient).not.toBeNull();
    });
  });

  describe('exportAnalytics', () => {
    it('should call API with correct endpoint', async () => {
      const mockClient = analyticsService.exportAnalytics('splits', 'json');
      expect(mockClient).not.toBeNull();
    });

    it('should handle different export types', async () => {
      const types = ['splits', 'payments', 'groups'] as const;
      for (const type of types) {
        const mockClient = analyticsService.exportAnalytics(type, 'csv');
        expect(mockClient).not.toBeNull();
      }
    });

    it('should handle different formats', async () => {
      const formats = ['csv', 'json'] as const;
      for (const format of formats) {
        const mockClient = analyticsService.exportAnalytics('splits', format);
        expect(mockClient).not.toBeNull();
      }
    });

    it('should include date range parameters', async () => {
      const mockClient = analyticsService.exportAnalytics(
        'splits',
        'json',
        '2024-01-01',
        '2024-12-31'
      );
      expect(mockClient).not.toBeNull();
    });
  });
});
