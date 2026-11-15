import { writable, derived } from 'svelte/store';

/** Online/offline state from navigator.onLine */
const online = writable(typeof navigator === 'undefined' ? true : navigator.onLine);

if (typeof window !== 'undefined') {
  window.addEventListener('online', () => online.set(true));
  window.addEventListener('offline', () => online.set(false));
}

export const isOffline = derived(online, ($online) => !$online);
