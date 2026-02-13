import { getIndexedDB, STORES } from './indexeddb';
import type { UploadReceiptResponse } from '$lib/types/api';

/** Offline action types */
export interface OfflineAction {
  id: string;
  type: 'receipt_upload' | 'split_calculate';
  data: unknown;
  createdAt: number;
  retryCount: number;
}

/** Action to enqueue (without id, createdAt, retryCount) */
export type EnqueueAction = Omit<OfflineAction, 'id' | 'createdAt' | 'retryCount'>;

/** Queued receipt upload action */
export interface QueuedReceiptUpload extends OfflineAction {
  type: 'receipt_upload';
  data: {
    file: File;
    onProgress?: (progress: number) => void;
  };
}

/** Queued split calculation action */
export interface QueuedSplitCalculate extends OfflineAction {
  type: 'split_calculate';
  data: {
    people: string[];
    items: any[];
    tax: number;
    tip: number;
  };
}

/** Offline queue service with Background Sync */
export class OfflineQueueService {
  private processing = false;

  /** Add action to queue */
  async enqueue(action: EnqueueAction): Promise<string> {
    const indexedDB = await getIndexedDB();
    const id = crypto.randomUUID();

    const queuedAction = {
      ...action,
      id,
      createdAt: Date.now(),
      retryCount: 0,
    };

    await indexedDB.add(STORES.OFFLINE_QUEUE, queuedAction);
    return id;
  }

  /** Process all queued actions */
  async processQueue(): Promise<void> {
    if (this.processing) return;

    this.processing = true;
    try {
      const indexedDB = await getIndexedDB();
      const actions = await indexedDB.getAll<OfflineAction>(STORES.OFFLINE_QUEUE);

      for (const action of actions) {
        try {
          await this.processAction(action);
          // Remove from queue on success
          await indexedDB.delete(STORES.OFFLINE_QUEUE, action.id);
        } catch (error) {
          console.error(`Failed to process action ${action.id}:`, error);
          // Update retry count
          action.retryCount++;
          await indexedDB.put(STORES.OFFLINE_QUEUE, action);
        }
      }
    } finally {
      this.processing = false;
    }
  }

  /** Process single action */
  private async processAction(action: OfflineAction): Promise<void> {
    switch (action.type) {
      case 'receipt_upload':
        return this.processReceiptUpload(action as QueuedReceiptUpload);
      case 'split_calculate':
        return this.processSplitCalculate(action as QueuedSplitCalculate);
      default:
        throw new Error(`Unknown action type: ${(action as any).type}`);
    }
  }

  /** Process queued receipt upload */
  private async processReceiptUpload(action: QueuedReceiptUpload): Promise<void> {
    // Import receiptsService dynamically to avoid circular dependency
    const { receiptsService } = await import('$lib/services/api/receipts');
    const result = await receiptsService.upload({
      file: action.data.file,
      onProgress: action.data.onProgress,
    });
    // Store result in IndexedDB
    const indexedDB = await getIndexedDB();
    await indexedDB.add(STORES.RECEIPTS, result.parsed_data);
  }

  /** Process queued split calculation */
  private async processSplitCalculate(action: QueuedSplitCalculate): Promise<void> {
    const { calculateSplit } = await import('$lib/services/offline/calc');
    const result = calculateSplit(
      action.data.people,
      action.data.items,
      (action.data as any).assignments || [],
      action.data.tax,
      action.data.tip,
      (action.data as any).split_evenly || false
    );
    // Store result in IndexedDB
    const indexedDB = await getIndexedDB();
    await indexedDB.add(STORES.SPLITS, result);
  }

  /** Get queued actions count */
  async getQueuedCount(): Promise<number> {
    const indexedDB = await getIndexedDB();
    return await indexedDB.count(STORES.OFFLINE_QUEUE);
  }

  /** Clear all queued actions */
  async clear(): Promise<void> {
    const indexedDB = await getIndexedDB();
    await indexedDB.clear(STORES.OFFLINE_QUEUE);
  }
}

/** Singleton instance */
let queueInstance: OfflineQueueService | null = null;

/** Initialize queue service */
export async function getOfflineQueue(): Promise<OfflineQueueService> {
  if (!queueInstance) {
    queueInstance = new OfflineQueueService();
  }
  return queueInstance;
}
