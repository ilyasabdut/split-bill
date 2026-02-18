import { writable, derived } from 'svelte/store';
import type { ReceiptData } from '$lib/types/receipt';

/** Receipt state interface */
interface ReceiptState {
  data: ReceiptData | null;
  loading: boolean;
  error: string | null;
  uploadProgress: number;
}

const initialState: ReceiptState = {
  data: null,
  loading: false,
  error: null,
  uploadProgress: 0
};

function createReceiptStore() {
  const { subscribe, update, set } = writable(initialState);

  return {
    subscribe,

    /** Get current receipt data */
    data: derived({ subscribe }, ($state) => $state.data),

    /** Check if loading */
    isLoading: derived({ subscribe }, ($state) => $state.loading),

    /** Get current error */
    error: derived({ subscribe }, ($state) => $state.error),

    /** Get upload progress */
    uploadProgress: derived({ subscribe }, ($state) => $state.uploadProgress),

    /** Start loading state */
    startLoading: () => update(state => ({
      ...state,
      loading: true,
      error: null,
      uploadProgress: 0
    })),

    /** Set receipt data */
    setData: (data: ReceiptData) => update(state => ({
      ...state,
      data,
      loading: false,
      error: null
    })),

    /** Set receipt data from manual input (for receipt page) */
    setReceipt: (receiptData: any) => update(state => ({
      ...state,
      data: {
        merchant_name: 'Manual Entry',
        items: receiptData.items.map((item: any) => ({
          name: item.name,
          price: item.price,
          quantity: 1
        })),
        total: receiptData.total,
        tax: receiptData.tax,
        currency: 'USD',
        date: new Date().toISOString()
      },
      loading: false,
      error: null
    })),

    /** Get current receipt data directly */
    getReceipt: () => {
      let currentData: ReceiptData | null = null;
      const unsubscribe = subscribe(state => {
        currentData = state.data;
      })();
      return currentData;
    },

    /** Set error state */
    setError: (error: string) => update(state => ({
      ...state,
      loading: false,
      error,
      data: null
    })),

    /** Update upload progress */
    setProgress: (progress: number) => update(state => ({
      ...state,
      uploadProgress: progress
    })),

    /** Reset to initial state */
    reset: () => set(initialState)
  };
}

export const receiptStore = createReceiptStore();
