import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { splitStore } from '../split';
import type { ReceiptItem } from '$lib/types/receipt';

describe('splitStore', () => {
  beforeEach(() => {
    splitStore.reset();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const state = get(splitStore);
      expect(state).toEqual({
        people: [],
        items: [],
        assignments: [],
        tax: 0,
        tip: 0,
        split_evenly: false,
        results: null,
        currency: 'IDR',
        payments: {},
        loading: false,
        error: null
      });
    });
  });

  describe('setCurrency', () => {
    it('should set currency', () => {
      splitStore.setCurrency('USD');
      expect(get(splitStore).currency).toBe('USD');
    });
  });

  describe('setPaymentStatus', () => {
    it('should set payment status for a person', () => {
      splitStore.setPaymentStatus('John', 'paid');
      expect(get(splitStore).payments.John).toBe('paid');

      splitStore.setPaymentStatus('Jane', 'pending');
      expect(get(splitStore).payments.Jane).toBe('pending');
    });

    it('should update existing payment status', () => {
      splitStore.setPaymentStatus('John', 'unpaid');
      expect(get(splitStore).payments.John).toBe('unpaid');

      splitStore.setPaymentStatus('John', 'paid');
      expect(get(splitStore).payments.John).toBe('paid');
    });
  });

  describe('setPeople', () => {
    it('should set people list', () => {
      const people = ['John', 'Jane', 'Bob'];
      splitStore.setPeople(people);
      expect(get(splitStore).people).toEqual(people);
    });
  });

  describe('addPerson', () => {
    it('should add a person', () => {
      splitStore.addPerson('John');
      expect(get(splitStore).people).toEqual(['John']);

      splitStore.addPerson('Jane');
      expect(get(splitStore).people).toEqual(['John', 'Jane']);
    });

    it('should not add duplicate people', () => {
      splitStore.addPerson('John');
      splitStore.addPerson('John');
      expect(get(splitStore).people).toEqual(['John', 'John']);
    });
  });

  describe('removePerson', () => {
    it('should remove a person', () => {
      splitStore.setPeople(['John', 'Jane', 'Bob']);
      splitStore.removePerson('Jane');
      expect(get(splitStore).people).toEqual(['John', 'Bob']);
    });

    it('should remove all instances of a person', () => {
      splitStore.setPeople(['John', 'Jane', 'John', 'Bob']);
      splitStore.removePerson('John');
      expect(get(splitStore).people).toEqual(['Jane', 'Bob']);
    });

    it('should handle removing non-existent person', () => {
      splitStore.setPeople(['John', 'Jane']);
      splitStore.removePerson('Bob');
      expect(get(splitStore).people).toEqual(['John', 'Jane']);
    });
  });

  describe('setItems', () => {
    it('should set items and create default assignments', () => {
      const items: ReceiptItem[] = [
        { name: 'Nasi Goreng', price: 50000, quantity: 1 },
        { name: 'Ayam Bakar', price: 75000, quantity: 1 }
      ];

      splitStore.setPeople(['John']);
      splitStore.setItems(items);

      const state = get(splitStore);
      expect(state.items).toEqual(items);
      expect(state.assignments).toEqual([
        { item_id: 'Nasi Goreng', assigned_to: ['John'] },
        { item_id: 'Ayam Bakar', assigned_to: ['John'] }
      ]);
    });

    it('should create empty assignments when no people', () => {
      const items: ReceiptItem[] = [
        { name: 'Nasi Goreng', price: 50000, quantity: 1 }
      ];

      splitStore.setItems(items);

      const state = get(splitStore);
      expect(state.assignments).toEqual([
        { item_id: 'Nasi Goreng', assigned_to: [] }
      ]);
    });

    it('should replace existing items and assignments', () => {
      const initialItems: ReceiptItem[] = [
        { name: 'Item 1', price: 10000, quantity: 1 }
      ];
      const newItems: ReceiptItem[] = [
        { name: 'Item 2', price: 20000, quantity: 1 }
      ];

      splitStore.setPeople(['John']);
      splitStore.setItems(initialItems);
      expect(get(splitStore).items).toEqual(initialItems);

      splitStore.setItems(newItems);
      const state = get(splitStore);
      expect(state.items).toEqual(newItems);
      expect(state.assignments).toEqual([
        { item_id: 'Item 2', assigned_to: ['John'] }
      ]);
    });
  });

  describe('updateAssignment', () => {
    beforeEach(() => {
      const items: ReceiptItem[] = [
        { name: 'Item 1', price: 10000, quantity: 1 },
        { name: 'Item 2', price: 20000, quantity: 1 }
      ];
      splitStore.setItems(items);
    });

    it('should update assignment for an item', () => {
      splitStore.updateAssignment('Item 1', ['John', 'Jane']);

      const state = get(splitStore);
      expect(state.assignments[0]).toEqual({
        item_id: 'Item 1',
        assigned_to: ['John', 'Jane']
      });
      expect(state.assignments[1].assigned_to).toEqual([]);
    });

    it('should not affect other assignments', () => {
      splitStore.updateAssignment('Item 1', ['John']);
      splitStore.updateAssignment('Item 2', ['Jane']);

      const state = get(splitStore);
      expect(state.assignments[0].assigned_to).toEqual(['John']);
      expect(state.assignments[1].assigned_to).toEqual(['Jane']);
    });

    it('should handle non-existent item', () => {
      splitStore.updateAssignment('Non-existent', ['John']);

      const state = get(splitStore);
      expect(state.assignments.length).toBe(2);
    });
  });

  describe('setTax', () => {
    it('should set tax amount', () => {
      splitStore.setTax(50000);
      expect(get(splitStore).tax).toBe(50000);

      splitStore.setTax(100000);
      expect(get(splitStore).tax).toBe(100000);
    });
  });

  describe('setTip', () => {
    it('should set tip amount', () => {
      splitStore.setTip(25000);
      expect(get(splitStore).tip).toBe(25000);

      splitStore.setTip(50000);
      expect(get(splitStore).tip).toBe(50000);
    });
  });

  describe('setSplitEvenly', () => {
    it('should set split evenly flag', () => {
      splitStore.setSplitEvenly(true);
      expect(get(splitStore).split_evenly).toBe(true);

      splitStore.setSplitEvenly(false);
      expect(get(splitStore).split_evenly).toBe(false);
    });
  });

  describe('setResults', () => {
    it('should set split results', () => {
      const results = {
        John: {
          total: 100000,
          items: [{ name: 'Item 1', price: 100000, quantity: 1 }],
          tax_share: 5000,
          tip_share: 5000
        },
        Jane: {
          total: 50000,
          items: [{ name: 'Item 2', price: 50000, quantity: 1 }],
          tax_share: 2500,
          tip_share: 2500
        }
      };

      splitStore.setResults(results);

      const state = get(splitStore);
      expect(state.results).toEqual(results);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('setLoading', () => {
    it('should set loading state', () => {
      splitStore.setLoading(true);
      expect(get(splitStore).loading).toBe(true);

      splitStore.setLoading(false);
      expect(get(splitStore).loading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should set error message', () => {
      const errorMessage = 'Failed to calculate split';
      splitStore.setError(errorMessage);

      const state = get(splitStore);
      expect(state.error).toBe(errorMessage);
      expect(state.loading).toBe(false);
    });

    it('should clear error when null is passed', () => {
      splitStore.setError('Some error');
      expect(get(splitStore).error).toBe('Some error');

      splitStore.setError(null);
      expect(get(splitStore).error).toBeNull();
    });
  });

  describe('totalForPerson', () => {
    it('should return total for person when results exist', () => {
      const results = {
        John: { total: 150000, items: [], tax_share: 7500, tip_share: 7500 },
        Jane: { total: 75000, items: [], tax_share: 3750, tip_share: 3750 }
      };

      splitStore.setResults(results);

      const johnTotal = get(splitStore.totalForPerson('John'));
      expect(johnTotal).toBe(150000);

      const janeTotal = get(splitStore.totalForPerson('Jane'));
      expect(janeTotal).toBe(75000);
    });

    it('should return 0 when no results', () => {
      const total = get(splitStore.totalForPerson('John'));
      expect(total).toBe(0);
    });

    it('should return 0 when person not in results', () => {
      const results = {
        John: { total: 100000, items: [], tax_share: 5000, tip_share: 5000 }
      };

      splitStore.setResults(results);
      const total = get(splitStore.totalForPerson('Jane'));
      expect(total).toBe(0);
    });
  });

  describe('selectors', () => {
    it('should select all derived values', () => {
      splitStore.setPeople(['John', 'Jane']);
      splitStore.setItems([{ name: 'Item 1', price: 50000, quantity: 1 }]);
      splitStore.setTax(5000);
      splitStore.setTip(5000);
      splitStore.setSplitEvenly(true);
      splitStore.setCurrency('USD');
      splitStore.setPaymentStatus('John', 'paid');

      expect(get(splitStore.people)).toEqual(['John', 'Jane']);
      expect(get(splitStore.items)).toEqual([{ name: 'Item 1', price: 50000, quantity: 1 }]);
      expect(get(splitStore.tax)).toBe(5000);
      expect(get(splitStore.tip)).toBe(5000);
      expect(get(splitStore.splitEvenly)).toBe(true);
      expect(get(splitStore.currency)).toBe('USD');
      expect(get(splitStore.payments)).toEqual({ John: 'paid' });
      expect(get(splitStore.isLoading)).toBe(false);
      expect(get(splitStore.error)).toBeNull();
    });
  });

  describe('reset', () => {
    it('should reset to initial state', () => {
      // Set some state
      splitStore.setPeople(['John', 'Jane']);
      splitStore.setItems([{ name: 'Item 1', price: 50000, quantity: 1 }]);
      splitStore.setTax(5000);
      splitStore.setTip(5000);
      splitStore.setSplitEvenly(true);
      splitStore.setCurrency('USD');
      splitStore.setResults({ John: { total: 100000, items: [], tax_share: 5000, tip_share: 5000 } });
      splitStore.setLoading(true);
      splitStore.setError('Test error');

      // Reset
      splitStore.reset();

      const state = get(splitStore);
      expect(state).toEqual({
        people: [],
        items: [],
        assignments: [],
        tax: 0,
        tip: 0,
        split_evenly: false,
        results: null,
        currency: 'IDR',
        payments: {},
        loading: false,
        error: null
      });
    });
  });
});
