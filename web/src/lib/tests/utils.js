// @ts-nocheck
import { render } from '@testing-library/svelte';
import { tick } from 'svelte';
import { vi } from 'vitest';

// Helper to wait for component updates
export async function waitForComponentUpdate() {
  await tick();
}

// Helper to test component props
export function testComponentProps(Component, defaultProps = {}) {
  return {
    render: (props = {}) => {
      return render(Component, { props: { ...defaultProps, ...props } });
    },

    testProp: (propName, propValue, testFn) => {
      const { container } = render(Component, {
        props: { ...defaultProps, [propName]: propValue }
      });
      testFn(container, propValue);
    }
  };
}

// Helper to mock fetch API
export function mockFetch(response, status = 200, headers = {}) {
  global.fetch = vi.fn().mockResolvedValue({
    status,
    headers: new Headers(headers),
    json: async () => response,
    text: async () => JSON.stringify(response),
    ok: status >= 200 && status < 300
  });
}

// Helper to mock fetch with error
export function mockFetchError(error, status = 500) {
  global.fetch = vi.fn().mockRejectedValue(error);
}

// Helper to create mock stores
export function createMockStore(initialValue) {
  let value = initialValue;
  const subscribers = new Set();

  return {
    subscribe: (fn) => {
      subscribers.add(fn);
      fn(value);
      return () => subscribers.delete(fn);
    },
    set: (newValue) => {
      value = newValue;
      subscribers.forEach(fn => fn(value));
    },
    update: (fn) => {
      value = fn(value);
      subscribers.forEach(sub => fn(value));
    }
  };
}

// Helper to test store behavior
export function testStore(store, initialValue) {
  let currentValue;
  const unsubscribe = store.subscribe(value => {
    currentValue = value;
  });

  return {
    getValue: () => currentValue,
    cleanup: unsubscribe,
    expectValue: (expectedValue) => {
      expect(currentValue).toEqual(expectedValue);
    }
  };
}

// Helper to create test data
export const testData = {
  user: {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    api_key: 'test-api-key'
  },

  group: {
    id: 1,
    name: 'Test Group',
    owner_id: 1,
    created_at: new Date().toISOString()
  },

  split: {
    id: 1,
    group_id: 1,
    owner_id: 1,
    receipt_data: {
      items: [
        { name: 'Pizza', price: 20.0, quantity: 1 },
        { name: 'Drinks', price: 10.0, quantity: 2 }
      ],
      tax: 3.0,
      tip: 5.0,
      total: 48.0
    },
    split_results: {
      'Alice': 24.0,
      'Bob': 24.0
    },
    currency: 'USD',
    status: 'pending',
    created_at: new Date().toISOString()
  },

  payment: {
    id: 1,
    split_id: 1,
    person_name: 'Alice',
    amount: 24.0,
    currency: 'USD',
    status: 'pending',
    confirmed_at: null
  },

  template: {
    id: 1,
    user_id: 1,
    name: 'Even Split Template',
    config: {
      type: 'even',
      settings: {
        include_tax: true,
        include_tip: true
      }
    },
    created_at: new Date().toISOString()
  },

  currencyRate: {
    id: 1,
    from_currency: 'USD',
    to_currency: 'EUR',
    rate: 0.85,
    updated_at: new Date().toISOString()
  }
};

// Helper to create mock IndexedDB data
export async function createMockIndexedDBData(dbName, storeName, data) {
  const db = await new Promise((resolve, reject) => {
    const request = indexedDB.open(dbName, 1);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(storeName)) {
        db.createObjectStore(storeName, { keyPath: 'id' });
      }
    };
  });

  const transaction = db.transaction([storeName], 'readwrite');
  const store = transaction.objectStore(storeName);

  for (const item of data) {
    await store.put(item);
  }

  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
}

// Helper to test async functions
export async function testAsync(fn, expectedError) {
  try {
    await fn();
    if (expectedError) {
      throw new Error('Expected function to throw, but it did not');
    }
  } catch (error) {
    if (expectedError) {
      expect(error).toEqual(expectedError);
    } else {
      throw error;
    }
  }
}

// Helper to test event handlers
export function createMockEvent(data = {}) {
  return {
    preventDefault: () => {},
    stopPropagation: () => {},
    target: { value: '', ...data },
    currentTarget: { value: '', ...data },
    ...data
  };
}

// Helper to test file uploads
export function createMockFile(name, size, type) {
  const blob = new Blob([new ArrayBuffer(size)], { type });
  blob.lastModified = Date.now();
  blob.name = name;
  return blob;
}

// Helper to test responsive behavior
export function mockMediaQuery(query, matches) {
  const mediaQueryList = {
    matches,
    media: query,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn()
  };

  window.matchMedia = vi.fn().mockReturnValue(mediaQueryList);

  return mediaQueryList;
}

// Helper to test localStorage/sessionStorage
export function createMockStorage() {
  let store = {};

  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: vi.fn((key) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: vi.fn((index) => Object.keys(store)[index] || null)
  };
}
