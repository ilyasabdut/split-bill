import type { ReceiptData } from './receipt';

/** Split calculation results */
export interface SplitResults {
  [personName: string]: PersonSplit;
}

/** Individual person's split */
export interface PersonSplit {
  total: number;
  items: AssignedItem[];
  tax_share: number;
  tip_share: number;
}

/** Item assigned to a person */
export interface AssignedItem {
  name: string;
  price: number;
  quantity: number;
}

/** Split state for store */
export interface SplitState {
  people: string[];
  items: ReceiptItem[];
  assignments: ItemAssignment[];
  tax: number;
  tip: number;
  split_evenly: boolean;
  results: SplitResults | null;
  currency: string;
  payments: Record<string, 'unpaid' | 'pending' | 'paid'>;
  loading: boolean;
  error: string | null;
}

import type { ReceiptItem } from './receipt';
import type { ItemAssignment } from './receipt';
