/** IndexedDB database name and version */
const DB_NAME = 'split-bill-db';
const DB_VERSION = 2;

/** Store names */
export const STORES = {
  RECEIPTS: 'receipts',
  SPLITS: 'splits',
  OFFLINE_QUEUE: 'offline_queue',
  GROUPS: 'groups',
  TEMPLATES: 'templates',
  CURRENCY_RATES: 'currency_rates',
} as const;

/** IndexedDB wrapper with LRU eviction and error handling */
export class IndexedDBService {
  private db: IDBDatabase | null = null;

  /** Initialize database */
  async init(): Promise<void> {
    if (this.db) return;

    return new Promise<void>((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create stores if they don't exist
        if (!db.objectStoreNames.contains(STORES.RECEIPTS)) {
          db.createObjectStore(STORES.RECEIPTS, { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains(STORES.SPLITS)) {
          db.createObjectStore(STORES.SPLITS, { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains(STORES.OFFLINE_QUEUE)) {
          db.createObjectStore(STORES.OFFLINE_QUEUE, { keyPath: 'id', autoIncrement: true });
        }
        if (!db.objectStoreNames.contains(STORES.GROUPS)) {
          db.createObjectStore(STORES.GROUPS, { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains(STORES.TEMPLATES)) {
          db.createObjectStore(STORES.TEMPLATES, { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains(STORES.CURRENCY_RATES)) {
          db.createObjectStore(STORES.CURRENCY_RATES, { keyPath: 'currency' });
        }
      };

      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
    });
  }

  /** Close database */
  close(): void {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }

  /** Get store */
  private getStore(storeName: string, mode: IDBTransactionMode = 'readonly'): IDBObjectStore {
    if (!this.db) throw new Error('Database not initialized');

    const transaction = this.db.transaction(storeName, mode);
    return transaction.objectStore(storeName);
  }

  /** Add item to store */
  async add<T>(storeName: string, value: T): Promise<IDBValidKey> {
    const store = this.getStore(storeName, 'readwrite');
    const request = store.add(value);

    return new Promise<IDBValidKey>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /** Update item in store */
  async put<T>(storeName: string, value: T): Promise<IDBValidKey> {
    const store = this.getStore(storeName, 'readwrite');
    const request = store.put(value);

    return new Promise<IDBValidKey>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /** Get item by key */
  async get<T>(storeName: string, key: string): Promise<T | null> {
    const store = this.getStore(storeName, 'readonly');
    const request = store.get(key);

    return new Promise<T | null>((resolve) => {
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => resolve(null);
    });
  }

  /** Get all items from store */
  async getAll<T>(storeName: string): Promise<T[]> {
    const store = this.getStore(storeName, 'readonly');
    const request = store.getAll();

    return new Promise<T[]>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  /** Delete item by key */
  async delete(storeName: string, key: string): Promise<void> {
    const store = this.getStore(storeName, 'readwrite');
    const request = store.delete(key);

    return new Promise<void>((resolve, reject) => {
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /** Clear all items from store */
  async clear(storeName: string): Promise<void> {
    const store = this.getStore(storeName, 'readwrite');
    const request = store.clear();

    return new Promise<void>((resolve, reject) => {
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /** Count items in store */
  async count(storeName: string): Promise<number> {
    const store = this.getStore(storeName, 'readonly');
    const request = store.count();

    return new Promise<number>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result || 0);
      request.onerror = () => reject(request.error);
    });
  }

  /** LRU eviction: Remove oldest items when quota exceeded */
  async enforceQuota(storeName: string, maxItems: number): Promise<void> {
    const count = await this.count(storeName);
    if (count > maxItems) {
      const items = await this.getAll(storeName);
      // Sort by timestamp (assuming items have createdAt)
      const sorted = items.sort((a: any, b: any) =>
        (a.createdAt || 0) - (b.createdAt || 0)
      );
      // Remove oldest items
      const toRemove = sorted.slice(0, count - maxItems);
      const store = this.getStore(storeName, 'readwrite');

      for (const item of toRemove) {
        store.delete((item as any).id);
      }
    }
  }
}

/** Singleton instance */
let indexedDBInstance: IndexedDBService | null = null;

/** Initialize IndexedDB service */
export async function getIndexedDB(): Promise<IndexedDBService> {
  if (!indexedDBInstance) {
    indexedDBInstance = new IndexedDBService();
    await indexedDBInstance.init();
  }
  return indexedDBInstance;
}
