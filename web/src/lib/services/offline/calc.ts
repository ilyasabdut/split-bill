import type { PersonSplit } from '$lib/types/split';

export type RoundingMode = 'down' | 'exact' | 'up';
export type SplitMethod = 'equal' | 'percentage' | 'item';

/** Item with the indexes of the people sharing it */
export interface SplitItem {
  name: string;
  price: number;
  assignedTo: number[];
}

export interface SplitInput {
  peopleCount: number;
  billAmount: number;
  tax: number;
  tip: number;
  method: SplitMethod;
  /** One per person, used by the 'percentage' method */
  percentages?: number[];
  /** Used by the 'item' method; with no items it falls back to an equal split */
  items?: SplitItem[];
  rounding?: RoundingMode;
}

const ROUNDING_UNIT = 1000;

/** 'exact' rounds to a whole unit of currency, 'up'/'down' to the nearest 1000 */
export function applyRounding(amount: number, mode: RoundingMode = 'exact'): number {
  if (mode === 'exact') return Math.round(amount);
  if (mode === 'up') return Math.ceil(amount / ROUNDING_UNIT) * ROUNDING_UNIT;
  return Math.floor(amount / ROUNDING_UNIT) * ROUNDING_UNIT;
}

/** Calculate each person's share, in the same order as the people */
export function calculateSplit(input: SplitInput): PersonSplit[] {
  const { peopleCount, billAmount, tax, tip, method, percentages = [], items = [], rounding } = input;
  const byItem = method === 'item' && items.length > 0;

  // Each person's fraction of the bill; tax and tip follow the same fraction
  let base = billAmount;
  let fractions: number[];
  if (method === 'percentage') {
    fractions = Array.from({ length: peopleCount }, (_, i) => (percentages[i] ?? 0) / 100);
  } else if (byItem) {
    const shares = Array.from({ length: peopleCount }, () => 0);
    for (const item of items) {
      for (const person of item.assignedTo) {
        shares[person] += item.price / item.assignedTo.length;
      }
    }
    base = shares.reduce((sum, share) => sum + share, 0);
    fractions = shares.map(share => (base > 0 ? share / base : 0));
  } else {
    fractions = Array.from({ length: peopleCount }, () => 1 / peopleCount);
  }

  return fractions.map((fraction, person) => ({
    total: applyRounding(fraction * (base + tax + tip), rounding),
    items: byItem
      ? items
          .filter(item => item.assignedTo.includes(person))
          .map(item => ({ name: item.name, price: item.price, quantity: 1 }))
      : [],
    tax_share: Math.round(fraction * tax),
    tip_share: Math.round(fraction * tip)
  }));
}
