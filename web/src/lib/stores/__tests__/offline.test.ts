import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { offlineStore, isOffline, hasQueuedActions } from '../offline';

describe('offlineStore', () => {
  beforeEach(() => {
    // Reset is not available on offlineStore, so we test the methods
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = get(offlineStore);
      expect(state.online).toBe(true);
      expect(state.queuedActions).toBe(0);
    });
  });

  describe('incrementQueued', () => {
    it('should increment queued actions count', () => {
      const initialCount = get(offlineStore).queuedActions;
      offlineStore.incrementQueued();

      const newCount = get(offlineStore).queuedActions;
      expect(newCount).toBe(initialCount + 1);
    });

    it('should increment multiple times', () => {
      const initialCount = get(offlineStore).queuedActions;

      offlineStore.incrementQueued();
      offlineStore.incrementQueued();
      offlineStore.incrementQueued();

      const newCount = get(offlineStore).queuedActions;
      expect(newCount).toBe(initialCount + 3);
    });
  });

  describe('decrementQueued', () => {
    it('should decrement queued actions count', () => {
      // Set up some queued actions
      offlineStore.incrementQueued();
      offlineStore.incrementQueued();

      const initialCount = get(offlineStore).queuedActions;
      offlineStore.decrementQueued();

      const newCount = get(offlineStore).queuedActions;
      expect(newCount).toBe(initialCount - 1);
    });

    it('should not go below zero', () => {
      offlineStore.decrementQueued();

      const count = get(offlineStore).queuedActions;
      expect(count).toBeGreaterThanOrEqual(0);
    });
  });

  describe('resetQueued', () => {
    it('should reset queued actions to zero', () => {
      // Set up some queued actions
      offlineStore.incrementQueued();
      offlineStore.incrementQueued();
      offlineStore.incrementQueued();

      offlineStore.resetQueued();

      const count = get(offlineStore).queuedActions;
      expect(count).toBe(0);
    });
  });

  describe('setOnline', () => {
    it('should set online status', () => {
      offlineStore.setOnline(false);
      expect(get(offlineStore).online).toBe(false);

      offlineStore.setOnline(true);
      expect(get(offlineStore).online).toBe(true);
    });
  });

  describe('selectors', () => {
    it('should select online status', () => {
      offlineStore.setOnline(true);
      const online = get(offlineStore.isOnline);
      expect(online).toBe(true);

      offlineStore.setOnline(false);
      const offline = get(offlineStore.isOnline);
      expect(offline).toBe(false);
    });

    it('should select queued actions count', () => {
      offlineStore.incrementQueued();
      offlineStore.incrementQueued();

      const count = get(offlineStore.getQueuedActions);
      expect(count).toBe(2);
    });
  });

  describe('derived stores', () => {
    it('isOffline should be opposite of online', () => {
      offlineStore.setOnline(true);
      expect(get(isOffline)).toBe(false);

      offlineStore.setOnline(false);
      expect(get(isOffline)).toBe(true);
    });

    it('hasQueuedActions should be true when queued > 0', () => {
      offlineStore.resetQueued();
      expect(get(hasQueuedActions)).toBe(false);

      offlineStore.incrementQueued();
      expect(get(hasQueuedActions)).toBe(true);
    });

    it('hasQueuedActions should be false when queued is 0', () => {
      offlineStore.resetQueued();
      expect(get(hasQueuedActions)).toBe(false);
    });
  });
});
