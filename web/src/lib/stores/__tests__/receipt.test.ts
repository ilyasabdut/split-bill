import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { receiptStore } from '../receipt';

describe('receiptStore', () => {
  beforeEach(() => {
    receiptStore.reset();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = get(receiptStore);
      expect(state.data).toBeNull();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.uploadProgress).toBe(0);
    });
  });

  describe('startLoading', () => {
    it('should set loading state and reset error and progress', () => {
      receiptStore.startLoading();

      const state = get(receiptStore);
      expect(state.loading).toBe(true);
      expect(state.error).toBeNull();
      expect(state.uploadProgress).toBe(0);
    });
  });

  describe('setData', () => {
    it('should set receipt data and clear loading/error', () => {
      const receiptData = {
        merchant: 'Test Merchant',
        date: '2024-01-01',
        items: [],
        subtotal: 0,
        tax: 0,
        total: 0,
      };

      receiptStore.setData(receiptData);

      const state = get(receiptStore);
      expect(state.data).toEqual(receiptData);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('setError', () => {
    it('should set error message and clear data', () => {
      const errorMessage = 'Failed to process receipt';

      receiptStore.setError(errorMessage);

      const state = get(receiptStore);
      expect(state.error).toBe(errorMessage);
      expect(state.loading).toBe(false);
      expect(state.data).toBeNull();
    });
  });

  describe('setProgress', () => {
    it('should set upload progress', () => {
      receiptStore.setProgress(50);

      const state = get(receiptStore);
      expect(state.uploadProgress).toBe(50);
    });

    it('should handle progress from 0 to 100', () => {
      receiptStore.setProgress(0);
      expect(get(receiptStore).uploadProgress).toBe(0);

      receiptStore.setProgress(100);
      expect(get(receiptStore).uploadProgress).toBe(100);
    });

    it('should handle decimal progress values', () => {
      receiptStore.setProgress(25.5);
      expect(get(receiptStore).uploadProgress).toBe(25.5);
    });
  });

  describe('selectors', () => {
    it('should select receipt data', () => {
      const receiptData = {
        merchant: 'Test Merchant',
        date: '2024-01-01',
        items: [],
        subtotal: 0,
        tax: 0,
        total: 0,
      };

      receiptStore.setData(receiptData);

      const data = get(receiptStore.data);
      expect(data).toEqual(receiptData);
    });

    it('should select loading state', () => {
      receiptStore.startLoading();
      const loading = get(receiptStore.isLoading);
      expect(loading).toBe(true);
    });

    it('should select error', () => {
      receiptStore.setError('Test error');
      const error = get(receiptStore.error);
      expect(error).toBe('Test error');
    });

    it('should select upload progress', () => {
      receiptStore.setProgress(75);
      const progress = get(receiptStore.uploadProgress);
      expect(progress).toBe(75);
    });
  });

  describe('reset', () => {
    it('should reset to initial state', () => {
      // Set some state
      receiptStore.startLoading();
      receiptStore.setProgress(50);
      receiptStore.setError('TestError');

      // Reset
      receiptStore.reset();

      const state = get(receiptStore);
      expect(state).toEqual({
        data: null,
        loading: false,
        error: null,
        uploadProgress: 0
      });
    });
  });
});

