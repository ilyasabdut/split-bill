import { writable, derived } from 'svelte/store';
import type { SplitState, SplitResults } from '$lib/types/split';
import type { ReceiptItem, ItemAssignment } from '$lib/types/receipt';

const initialState: SplitState = {
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
};

function createSplitStore() {
  const { subscribe, update, set } = writable(initialState);

  return {
    subscribe,

    /** Get current state */
    people: derived({ subscribe }, ($state) => $state.people),
    items: derived({ subscribe }, ($state) => $state.items),
    assignments: derived({ subscribe }, ($state) => $state.assignments),
    tax: derived({ subscribe }, ($state) => $state.tax),
    tip: derived({ subscribe }, ($state) => $state.tip),
    splitEvenly: derived({ subscribe }, ($state) => $state.split_evenly),
    results: derived({ subscribe }, ($state) => $state.results),
    currency: derived({ subscribe }, ($state) => $state.currency),
    payments: derived({ subscribe }, ($state) => $state.payments),
    isLoading: derived({ subscribe }, ($state) => $state.loading),
    error: derived({ subscribe }, ($state) => $state.error),

    /** Set currency */
    setCurrency: (currency: string) => update(state => ({ ...state, currency })),

    /** Set payment status for a person */
    setPaymentStatus: (person: string, status: 'unpaid' | 'pending' | 'paid') => update(state => ({
      ...state,
      payments: { ...state.payments, [person]: status }
    })),

    /** Set people list */
    setPeople: (people: string[]) => update(state => ({ ...state, people })),

    /** Add a person */
    addPerson: (name: string) => update(state => ({
      ...state,
      people: [...state.people, name]
    })),

    /** Remove a person */
    removePerson: (name: string) => update(state => ({
      ...state,
      people: state.people.filter(p => p !== name)
    })),

    /** Set receipt items */
    setItems: (items: ReceiptItem[]) => update(state => ({
      ...state,
      items,
      // Create default assignments (each item assigned to first person or none)
      assignments: items.map(item => ({
        item_id: item.name,
        assigned_to: state.people.length > 0 ? [state.people[0]] : []
      }))
    })),

    /** Update item assignment */
    updateAssignment: (item_id: string, assigned_to: string[]) => update(state => ({
      ...state,
      assignments: state.assignments.map(a =>
        a.item_id === item_id ? { ...a, assigned_to } : a
      )
    })),

    /** Set tax amount */
    setTax: (tax: number) => update(state => ({ ...state, tax })),

    /** Set tip amount */
    setTip: (tip: number) => update(state => ({ ...state, tip })),

    /** Set split evenly flag */
    setSplitEvenly: (split_evenly: boolean) => update(state => ({
      ...state,
      split_evenly
    })),

    /** Set split results */
    setResults: (results: SplitResults) => update(state => ({
      ...state,
      results,
      loading: false,
      error: null
    })),

    /** Set loading state */
    setLoading: (loading: boolean) => update(state => ({ ...state, loading })),

    /** Set error state */
    setError: (error: string | null) => update(state => ({
      ...state,
      error,
      loading: false
    })),

    /** Reset to initial state */
    reset: () => set(initialState),

    /** Get recent splits (mock implementation) */
    async getRecentSplits(count: number = 5) {
      // This would fetch from API - for now returns empty array
      return [];
    },

    /** Get total for a specific person */
    totalForPerson: (person: string) => derived({ subscribe }, ($state) => {
      if (!$state.results || !$state.results[person]) {
        return 0;
      }
      return $state.results[person].total;
    }),
  }
}

export const splitStore = createSplitStore();
