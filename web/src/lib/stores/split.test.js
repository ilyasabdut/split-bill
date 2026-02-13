import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { splitStore } from './split';

describe('Split Store', () => {
  beforeEach(() => {
    // Reset store to initial state
    splitStore.reset();
  });

  describe('initialization', () => {
    it('should initialize with default values', () => {
      expect(get(splitStore.people)).toEqual([]);
      expect(get(splitStore.items)).toEqual([]);
      expect(get(splitStore.assignments)).toEqual([]);
      expect(get(splitStore.tax)).toBe(0);
      expect(get(splitStore.tip)).toBe(0);
      expect(get(splitStore.splitEvenly)).toBe(false);
      expect(get(splitStore.results)).toBe(null);
      expect(get(splitStore.currency)).toBe('IDR');
      expect(get(splitStore.payments)).toEqual({});
      expect(get(splitStore.isLoading)).toBe(false);
      expect(get(splitStore.error)).toBe(null);
    });
  });

  describe('people management', () => {
    it('should add a person', () => {
      splitStore.addPerson('Alice');

      const people = get(splitStore.people);
      expect(people).toEqual(['Alice']);
    });

    it('should add multiple people', () => {
      splitStore.addPerson('Alice');
      splitStore.addPerson('Bob');
      splitStore.addPerson('Charlie');

      const people = get(splitStore.people);
      expect(people).toEqual(['Alice', 'Bob', 'Charlie']);
    });

    it('should remove a person', () => {
      splitStore.addPerson('Alice');
      splitStore.addPerson('Bob');

      splitStore.removePerson('Alice');

      const people = get(splitStore.people);
      expect(people).toEqual(['Bob']);
    });

    it('should handle removing non-existent person', () => {
      splitStore.addPerson('Alice');

      splitStore.removePerson('Bob');

      const people = get(splitStore.people);
      expect(people).toEqual(['Alice']);
    });

    it('should set people list', () => {
      const newPeople = ['Alice', 'Bob', 'Charlie'];
      splitStore.setPeople(newPeople);

      expect(get(splitStore.people)).toEqual(newPeople);
    });
  });

  describe('items management', () => {
    it('should set items', () => {
      const items = [
        { name: 'Pizza', price: 20, quantity: 1 },
        { name: 'Drinks', price: 5, quantity: 2 }
      ];

      splitStore.setItems(items);

      expect(get(splitStore.items)).toEqual(items);
    });

    it('should create default assignments when setting items', () => {
      splitStore.addPerson('Alice');
      splitStore.addPerson('Bob');

      const items = [
        { name: 'Pizza', price: 20, quantity: 1 },
        { name: 'Drinks', price: 5, quantity: 2 }
      ];

      splitStore.setItems(items);

      const assignments = get(splitStore.assignments);
      expect(assignments).toHaveLength(2);
      expect(assignments[0]).toEqual({
        item_id: 'Pizza',
        assigned_to: ['Alice']
      });
      expect(assignments[1]).toEqual({
        item_id: 'Drinks',
        assigned_to: ['Alice']
      });
    });

    it('should handle empty people when setting items', () => {
      const items = [
        { name: 'Pizza', price: 20, quantity: 1 }
      ];

      splitStore.setItems(items);

      const assignments = get(splitStore.assignments);
      expect(assignments[0].assigned_to).toEqual([]);
    });
  });

  describe('assignments management', () => {
    beforeEach(() => {
      splitStore.addPerson('Alice');
      splitStore.addPerson('Bob');

      const items = [
        { name: 'Pizza', price: 20, quantity: 1 },
        { name: 'Drinks', price: 5, quantity: 2 }
      ];
      splitStore.setItems(items);
    });

    it('should update item assignment', () => {
      splitStore.updateAssignment('Pizza', ['Alice', 'Bob']);

      const assignments = get(splitStore.assignments);
      const pizzaAssignment = assignments.find(a => a.item_id === 'Pizza');
      expect(pizzaAssignment.assigned_to).toEqual(['Alice', 'Bob']);
    });

    it('should handle updating non-existent item', () => {
      splitStore.updateAssignment('Salad', ['Alice']);

      const assignments = get(splitStore.assignments);
      expect(assignments).toHaveLength(2); // No new assignment created
    });
  });

  describe('tax and tip management', () => {
    it('should set tax', () => {
      splitStore.setTax(5);
      expect(get(splitStore.tax)).toBe(5);

      splitStore.setTax(10.5);
      expect(get(splitStore.tax)).toBe(10.5);
    });

    it('should set tip', () => {
      splitStore.setTip(3);
      expect(get(splitStore.tip)).toBe(3);

      splitStore.setTip(7.25);
      expect(get(splitStore.tip)).toBe(7.25);
    });
  });

  describe('split settings', () => {
    it('should set split evenly flag', () => {
      splitStore.setSplitEvenly(true);
      expect(get(splitStore.splitEvenly)).toBe(true);

      splitStore.setSplitEvenly(false);
      expect(get(splitStore.splitEvenly)).toBe(false);
    });
  });

  describe('currency management', () => {
    it('should set currency', () => {
      splitStore.setCurrency('USD');
      expect(get(splitStore.currency)).toBe('USD');

      splitStore.setCurrency('EUR');
      expect(get(splitStore.currency)).toBe('EUR');
    });
  });

  describe('results management', () => {
    it('should set results', () => {
      const results = {
        Alice: { total: 25, items: [{ name: 'Pizza', amount: 20 }] },
        Bob: { total: 10, items: [{ name: 'Drinks', amount: 10 }] }
      };

      splitStore.setResults(results);

      expect(get(splitStore.results)).toEqual(results);
    });

    it('should set loading to false when setting results', () => {
      splitStore.setLoading(true);
      expect(get(splitStore.isLoading)).toBe(true);

      splitStore.setResults({});
      expect(get(splitStore.isLoading)).toBe(false);
    });
  });

  describe('payment status', () => {
    it('should set payment status', () => {
      splitStore.setPaymentStatus('Alice', 'paid');
      expect(get(splitStore.payments)).toEqual({ Alice: 'paid' });

      splitStore.setPaymentStatus('Bob', 'pending');
      expect(get(splitStore.payments)).toEqual({
        Alice: 'paid',
        Bob: 'pending'
      });
    });

    it('should update existing payment status', () => {
      splitStore.setPaymentStatus('Alice', 'pending');
      expect(get(splitStore.payments)).toEqual({ Alice: 'pending' });

      splitStore.setPaymentStatus('Alice', 'paid');
      expect(get(splitStore.payments)).toEqual({ Alice: 'paid' });
    });
  });

  describe('loading and error states', () => {
    it('should set loading state', () => {
      splitStore.setLoading(true);
      expect(get(splitStore.isLoading)).toBe(true);

      splitStore.setLoading(false);
      expect(get(splitStore.isLoading)).toBe(false);
    });

    it('should set error state', () => {
      splitStore.setError('Something went wrong');
      expect(get(splitStore.error)).toBe('Something went wrong');
      expect(get(splitStore.isLoading)).toBe(false);
    });

    it('should clear error state', () => {
      splitStore.setError('Something went wrong');
      expect(get(splitStore.error)).toBe('Something went wrong');

      splitStore.setError(null);
      expect(get(splitStore.error)).toBe(null);
    });
  });

  describe('reset functionality', () => {
    it('should reset all values to initial state', () => {
      // Set some values
      splitStore.addPerson('Alice');
      splitStore.setItems([{ name: 'Pizza', price: 20, quantity: 1 }]);
      splitStore.setTax(5);
      splitStore.setTip(3);
      splitStore.setCurrency('USD');
      splitStore.setSplitEvenly(true);
      splitStore.setResults({ Alice: { total: 25 } });
      splitStore.setPaymentStatus('Alice', 'paid');
      splitStore.setLoading(true);
      splitStore.setError('Error');

      // Verify values are set
      expect(get(splitStore.people)).toHaveLength(1);
      expect(get(splitStore.items)).toHaveLength(1);
      expect(get(splitStore.tax)).toBe(5);
      expect(get(splitStore.tip)).toBe(3);
      expect(get(splitStore.currency)).toBe('USD');
      expect(get(splitStore.splitEvenly)).toBe(true);
      expect(get(splitStore.results)).toBeTruthy();
      expect(get(splitStore.payments)).toEqual({ Alice: 'paid' });
      expect(get(splitStore.isLoading)).toBe(true);
      expect(get(splitStore.error)).toBe('Error');

      // Reset
      splitStore.reset();

      // Verify reset
      expect(get(splitStore.people)).toEqual([]);
      expect(get(splitStore.items)).toEqual([]);
      expect(get(splitStore.assignments)).toEqual([]);
      expect(get(splitStore.tax)).toBe(0);
      expect(get(splitStore.tip)).toBe(0);
      expect(get(splitStore.splitEvenly)).toBe(false);
      expect(get(splitStore.results)).toBe(null);
      expect(get(splitStore.currency)).toBe('IDR');
      expect(get(splitStore.payments)).toEqual({});
      expect(get(splitStore.isLoading)).toBe(false);
      expect(get(splitStore.error)).toBe(null);
    });
  });

  describe('derived stores', () => {
    it('should calculate total for person', () => {
      const results = {
        Alice: { total: 25, items: [{ name: 'Pizza', amount: 20 }] },
        Bob: { total: 10, items: [{ name: 'Drinks', amount: 10 }] }
      };
      splitStore.setResults(results);

      const aliceTotal = get(splitStore.totalForPerson('Alice'));
      expect(aliceTotal).toBe(25);

      const bobTotal = get(splitStore.totalForPerson('Bob'));
      expect(bobTotal).toBe(10);

      const charlieTotal = get(splitStore.totalForPerson('Charlie'));
      expect(charlieTotal).toBe(0);
    });

    it('should return 0 when no results', () => {
      const aliceTotal = get(splitStore.totalForPerson('Alice'));
      expect(aliceTotal).toBe(0);
    });
  });
});
