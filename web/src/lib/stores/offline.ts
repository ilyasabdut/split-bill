import { writable, derived } from 'svelte/store';

/** Online/offline state */
interface OfflineState {
  online: boolean;
  queuedActions: number;
}

const initialState: OfflineState = {
  online: true,
  queuedActions: 0
};

function createOfflineStore() {
  const { subscribe, update, set } = writable(initialState);

  // Initialize online status from navigator
  if (typeof window !== 'undefined' && window.navigator) {
    set({ ...initialState, online: navigator.onLine });

    // Listen for online/offline events
    window.addEventListener('online', async () => {
      update(state => ({ ...state, online: true }));
      const { getOfflineQueue } = await import('$lib/services/offline/queue');
      const queue = await getOfflineQueue();
      await queue.processQueue();
    });

    window.addEventListener('offline', () => {
      update(state => ({ ...state, online: false }));
    });
  }

  return {
    subscribe,

    /** Check if currently online */
    isOnline: derived({ subscribe }, ($state) => $state.online),

    /** Get number of queued actions */
    getQueuedActions: derived({ subscribe }, ($state) => $state.queuedActions),

    /** Increment queued actions count */
    incrementQueued: () => update(state => ({
      ...state,
      queuedActions: state.queuedActions + 1
    })),

    /** Decrement queued actions count */
    decrementQueued: () => update(state => ({
      ...state,
      queuedActions: Math.max(0, state.queuedActions - 1)
    })),

    /** Reset queued actions count */
    resetQueued: () => update(state => ({
      ...state,
      queuedActions: 0
    })),

    /** Manually set online status */
    setOnline: (online: boolean) => update(state => ({
      ...state,
      online
    }))
  };
}

export const offlineStore = createOfflineStore();

// Derived stores
export const isOffline = derived(offlineStore, ($store) => !$store.online);
export const hasQueuedActions = derived(offlineStore, ($store) => $store.queuedActions > 0);
