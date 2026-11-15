import { describe, it, expect } from 'vitest';
import { get } from 'svelte/store';
import { isOffline } from '../offline';

describe('isOffline', () => {
  it('follows browser online/offline events', () => {
    expect(get(isOffline)).toBe(false);

    window.dispatchEvent(new Event('offline'));
    expect(get(isOffline)).toBe(true);

    window.dispatchEvent(new Event('online'));
    expect(get(isOffline)).toBe(false);
  });
});
