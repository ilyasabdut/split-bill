import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { get } from 'svelte/store';
import { offlineStore, isOffline, hasQueuedActions } from './offline';

// Mock Background Sync API
const mockSync = {
  register: vi.fn(() => Promise.resolve()),
  getTags: vi.fn(() => Promise.resolve([]))
};

// Mock navigator.onLine
const originalOnLine = Object.getOwnPropertyDescriptor(window.navigator, 'onLine');

describe('Offline Store', () => {
  beforeEach(() => {
    // Reset store
    offlineStore.setOnline(true);
    offlineStore.resetQueued();

    // Mock navigator.onLine
    Object.defineProperty(window.navigator, 'onLine', {
      value: true,
      writable: true,
      configurable: true
    });

    // Mock service worker registration
    global.registration = {
      sync: mockSync
    };

    // Clear all mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Restore original navigator.onLine
    if (originalOnLine) {
      Object.defineProperty(window.navigator, 'onLine', originalOnLine);
    }
  });

  describe('online status', () => {
    it('should initialize with navigator.onLine value', () => {
      expect(get(offlineStore.isOnline)).toBe(true);
      expect(get(isOffline)).toBe(false);
    });

    it('should update online status', () => {
      offlineStore.setOnline(false);
      expect(get(offlineStore.isOnline)).toBe(false);
      expect(get(isOffline)).toBe(true);

      offlineStore.setOnline(true);
      expect(get(offlineStore.isOnline)).toBe(true);
      expect(get(isOffline)).toBe(false);
    });
  });

  describe('queued actions count', () => {
    it('should initialize with 0 queued actions', () => {
      expect(get(offlineStore.getQueuedActions)).toBe(0);
      expect(get(hasQueuedActions)).toBe(false);
    });

    it('should increment queued actions', () => {
      offlineStore.incrementQueued();
      expect(get(offlineStore.getQueuedActions)).toBe(1);
      expect(get(hasQueuedActions)).toBe(true);

      offlineStore.incrementQueued();
      expect(get(offlineStore.getQueuedActions)).toBe(2);
    });

    it('should decrement queued actions', () => {
      offlineStore.incrementQueued();
      offlineStore.incrementQueued();
      expect(get(offlineStore.getQueuedActions)).toBe(2);

      offlineStore.decrementQueued();
      expect(get(offlineStore.getQueuedActions)).toBe(1);

      offlineStore.decrementQueued();
      expect(get(offlineStore.getQueuedActions)).toBe(0);
      expect(get(hasQueuedActions)).toBe(false);
    });

    it('should not go below 0', () => {
      offlineStore.decrementQueued();
      expect(get(offlineStore.getQueuedActions)).toBe(0);
    });

    it('should reset queued actions', () => {
      offlineStore.incrementQueued();
      offlineStore.incrementQueued();
      offlineStore.incrementQueued();
      expect(get(offlineStore.getQueuedActions)).toBe(3);

      offlineStore.resetQueued();
      expect(get(offlineStore.getQueuedActions)).toBe(0);
      expect(get(hasQueuedActions)).toBe(false);
    });
  });

  describe('error handling', () => {
    it('should handle missing service worker registration', () => {
      // Remove service worker registration
      delete global.registration;

      // Should not throw error
      expect(() => {
        offlineStore.incrementQueued();
      }).not.toThrow();
    });
  });
});
