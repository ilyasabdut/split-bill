import { describe, it, expect } from 'vitest';
import { applyRounding, calculateSplit } from '../calc';

describe('applyRounding', () => {
  it('rounds to a whole unit, or up/down to the nearest 1000', () => {
    expect(applyRounding(1234.5)).toBe(1235);
    expect(applyRounding(1234.5, 'up')).toBe(2000);
    expect(applyRounding(1999, 'down')).toBe(1000);
    expect(applyRounding(3000, 'up')).toBe(3000);
  });
});

describe('calculateSplit', () => {
  const bill = { billAmount: 90000, tax: 9000, tip: 3000 };

  it('splits equally, tax and tip included', () => {
    const result = calculateSplit({ ...bill, peopleCount: 3, method: 'equal' });
    expect(result.map(p => p.total)).toEqual([34000, 34000, 34000]);
    expect(result[0]).toMatchObject({ tax_share: 3000, tip_share: 1000, items: [] });
  });

  it('splits by percentage', () => {
    const result = calculateSplit({ ...bill, peopleCount: 2, method: 'percentage', percentages: [75, 25] });
    expect(result.map(p => p.total)).toEqual([76500, 25500]);
    expect(result.map(p => p.tax_share)).toEqual([6750, 2250]);
  });

  it('splits by item, sharing items and spreading tax and tip proportionally', () => {
    const result = calculateSplit({
      billAmount: 0,
      tax: 10000,
      tip: 0,
      peopleCount: 3,
      method: 'item',
      items: [
        { name: 'Pizza', price: 60000, assignedTo: [0, 1] },
        { name: 'Soda', price: 20000, assignedTo: [1] },
        { name: 'Unclaimed', price: 99000, assignedTo: [] }
      ]
    });
    expect(result.map(p => p.total)).toEqual([33750, 56250, 0]);
    expect(result[1].items.map(i => i.name)).toEqual(['Pizza', 'Soda']);
    expect(result[2]).toMatchObject({ total: 0, tax_share: 0, items: [] });
  });

  it('falls back to an equal split when splitting by item without items', () => {
    const result = calculateSplit({ ...bill, peopleCount: 2, method: 'item' });
    expect(result.map(p => p.total)).toEqual([51000, 51000]);
  });

  it('applies the rounding mode to totals', () => {
    const input = { billAmount: 100000, tax: 0, tip: 0, peopleCount: 3, method: 'equal' as const };
    expect(calculateSplit({ ...input, rounding: 'up' })[0].total).toBe(34000);
    expect(calculateSplit({ ...input, rounding: 'down' })[0].total).toBe(33000);
    expect(calculateSplit({ ...input, rounding: 'exact' })[0].total).toBe(33333);
  });
});
