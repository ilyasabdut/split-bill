// @ts-nocheck
import '@testing-library/jest-dom';

// Mock IndexedDB
class MockIDBDatabase {
  constructor(name, version) {
    this.name = name;
    this.version = version;
    this.objectStoreNames = [];
    this.stores = new Map();
  }

  createObjectStore(name, options = {}) {
    const store = new MockIDBObjectStore(name, options);
    this.stores.set(name, store);
    this.objectStoreNames.push(name);
    return store;
  }

  transaction(storeNames, mode = 'readonly') {
    return new MockIDBTransaction(storeNames, mode, this);
  }

  close() {
    // No-op
  }
}

class MockIDBObjectStore {
  constructor(name, options = {}) {
    this.name = name;
    this.keyPath = options.keyPath;
    this.autoIncrement = options.autoIncrement;
    this.data = new Map();
    this.indexes = new Map();
  }

  add(value, key) {
    return new MockIDBRequest(() => {
      const actualKey = key || (this.keyPath ? value[this.keyPath] : value);
      if (this.data.has(actualKey)) {
        throw new Error('Key already exists');
      }
      this.data.set(actualKey, value);
      return actualKey;
    });
  }

  put(value, key) {
    return new MockIDBRequest(() => {
      const actualKey = key || (this.keyPath ? value[this.keyPath] : value);
      this.data.set(actualKey, value);
      return actualKey;
    });
  }

  get(key) {
    return new MockIDBRequest(() => {
      return this.data.get(key) || null;
    });
  }

  getAll() {
    return new MockIDBRequest(() => {
      return Array.from(this.data.values());
    });
  }

  getAllKeys() {
    return new MockIDBRequest(() => {
      return Array.from(this.data.keys());
    });
  }

  delete(key) {
    return new MockIDBRequest(() => {
      this.data.delete(key);
    });
  }

  clear() {
    return new MockIDBRequest(() => {
      this.data.clear();
    });
  }

  createIndex(name, keyPath, options = {}) {
    const index = new MockIDBIndex(name, keyPath, options);
    this.indexes.set(name, index);
    return index;
  }

  index(name) {
    return this.indexes.get(name);
  }
}

class MockIDBIndex {
  constructor(name, keyPath, options = {}) {
    this.name = name;
    this.keyPath = keyPath;
    this.unique = options.unique || false;
    this.multiEntry = options.multiEntry || false;
  }

  get(key) {
    // Simplified implementation
    return new MockIDBRequest(() => null);
  }

  getAll() {
    return new MockIDBRequest(() => []);
  }
}

class MockIDBTransaction {
  constructor(storeNames, mode, db) {
    this.storeNames = storeNames;
    this.mode = mode;
    this.db = db;
    this.completed = false;
  }

  objectStore(name) {
    const store = this.db.stores.get(name);
    if (!store) {
      throw new Error(`Object store ${name} not found`);
    }
    return store;
  }

  oncomplete() {}
  onerror() {}
  onabort() {}

  commit() {
    this.completed = true;
    setTimeout(() => this.oncomplete && this.oncomplete(), 0);
  }

  abort() {
    this.completed = true;
    setTimeout(() => this.onabort && this.onabort(), 0);
  }
}

class MockIDBRequest {
  constructor(executor) {
    this.result = undefined;
    this.error = null;
    this.readyState = 'pending';
    this.onsuccess = null;
    this.onerror = null;

    setTimeout(() => {
      try {
        this.result = executor();
        this.readyState = 'done';
        if (this.onsuccess) this.onsuccess({ target: this });
      } catch (error) {
        this.error = error;
        this.readyState = 'done';
        if (this.onerror) this.onerror({ target: this });
      }
    }, 0);
  }
}

class MockIDBFactory {
  constructor() {
    this.databases = new Map();
  }

  open(name, version) {
    return new MockIDBOpenDBRequest(name, version, this);
  }

  deleteDatabase(name) {
    return new MockIDBDeleteDBRequest(name, this);
  }
}

class MockIDBOpenDBRequest {
  constructor(name, version, factory) {
    this.name = name;
    this.version = version;
    this.factory = factory;
    this.result = null;
    this.error = null;
    this.onsuccess = null;
    this.onerror = null;
    this.onupgradeneeded = null;

    setTimeout(() => {
      try {
        let db = this.factory.databases.get(this.name);

        if (!db) {
          // Create new database
          db = new MockIDBDatabase(this.name, this.version || 1);
          this.factory.databases.set(this.name, db);

          if (this.onupgradeneeded) {
            this.result = db;
            this.onupgradeneeded({ target: this, oldVersion: 0, newVersion: this.version || 1 });
          }
        } else if (this.version && this.version > db.version) {
          // Upgrade database
          db.version = this.version;

          if (this.onupgradeneeded) {
            this.result = db;
            this.onupgradeneeded({ target: this, oldVersion: db.version, newVersion: this.version });
          }
        }

        this.result = db;
        if (this.onsuccess) this.onsuccess({ target: this });
      } catch (error) {
        this.error = error;
        if (this.onerror) this.onerror({ target: this });
      }
    }, 0);
  }
}

class MockIDBDeleteDBRequest {
  constructor(name, factory) {
    this.name = name;
    this.factory = factory;
    this.onsuccess = null;
    this.onerror = null;

    setTimeout(() => {
      try {
        this.factory.databases.delete(this.name);
        if (this.onsuccess) this.onsuccess({ target: this });
      } catch (error) {
        if (this.onerror) this.onerror({ target: this });
      }
    }, 0);
  }
}

// Set up global mocks
global.indexedDB = new MockIDBFactory();
global.IDBKeyRange = {
  only: (value) => ({ lower: value, upper: value }),
  bound: (lower, upper, lowerOpen, upperOpen) => ({
    lower,
    upper,
    lowerOpen: lowerOpen || false,
    upperOpen: upperOpen || false
  }),
  lowerBound: (lower, open) => ({
    lower,
    upper: null,
    lowerOpen: open || false,
    upperOpen: false
  }),
  upperBound: (upper, open) => ({
    lower: null,
    upper,
    lowerOpen: false,
    upperOpen: open || false
  }),
};

// Mock Background Sync API
global.registration = {
  sync: {
    register: () => Promise.resolve(),
    getTags: () => Promise.resolve([])
  }
};

// Mock navigator.onLine
global.navigator = {
  onLine: true,
  connection: {
    addEventListener: () => {},
    removeEventListener: () => {}
  }
};

// Mock window.matchMedia
global.matchMedia = (query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: () => {},
  removeListener: () => {},
  addEventListener: () => {},
  removeEventListener: () => {},
  dispatchEvent: () => {},
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock crypto.randomUUID
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    })
  },
  writable: true,
  configurable: true
});

// Clean up after each test
afterEach(() => {
  // Clear all IndexedDB databases
  global.indexedDB.databases.clear();

  // Reset navigator.onLine
  global.navigator.onLine = true;
});
