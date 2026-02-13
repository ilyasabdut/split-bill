/// <reference no-default="lib.webworker" />

declare const self: ServiceWorkerGlobalScope;
declare const CACHE_NAME = 'split-bill-api-cache';

// Install service worker on page load
if ('serviceWorker' in navigator) {
  const sw = navigator.serviceWorker;
  if (sw) {
    // Service worker is already registered
    console.log('[SW] Service worker already registered');
  } else {
    // Register service worker
    navigator.serviceWorker.register('/service-worker.js', { scope: '/' })
      .then(() => console.log('[SW] Service worker registered'))
      .catch(error => console.error('[SW] Service worker registration failed', error));
  }
}

// Listen for online/offline events
window.addEventListener('online', () => {
  console.log('[SW] Now online');
  self.dispatchEvent(new CustomEvent('offline-queue:sync'));
});

window.addEventListener('offline', () => {
  console.log('[SW] Now offline');
});

// Custom event for offline queue sync
class CustomEvent extends Event {
  constructor(name: string) {
    super(name);
  }
}

// Service worker message handler
self.addEventListener('message', (event: MessageEvent) => {
  if (event.data.type === 'SYNC_OFFLINE_QUEUE') {
    console.log('[SW] Processing offline queue...');
    processOfflineQueue();
  }
});

// Process offline queue
async function processOfflineQueue() {
  try {
    // Import queue and IndexedDB
    const { getOfflineQueue, getIndexedDB } = await import('$lib/services/offline');

    const queue = await getOfflineQueue();
    const indexedDB = await getIndexedDB();

    // Get all queued actions
    const actions = await queue.getAll();

    console.log(`[SW] Processing ${actions.length} queued actions`);

    for (const action of actions) {
      try {
        switch (action.type) {
          case 'receipt_upload':
            await processReceiptUpload(action);
            break;
          case 'split_calculate':
            await processSplitCalculate(action);
            break;
          default:
            console.warn(`[SW] Unknown action type: ${action.type}`);
        }

        // Remove from queue
        await indexedDB.delete('offline_queue', action.id);
      } catch (error) {
        console.error(`[SW] Failed to process action ${action.id}:`, error);
        // Update retry count
        action.retryCount = (action.retryCount || 0) + 1;
        await indexedDB.put('offline_queue', action);
      }
    }

    // Notify client about completion
    self.clients?.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        count: actions.length
      });
    });

    console.log('[SW] Offline queue processing complete');
  }
}

async function processReceiptUpload(action: any): Promise<void> {
  console.log('[SW] Processing receipt upload:', action);

  // Import needed services
  const { receiptsService, getOfflineQueue } = await import('$lib/services/api');
  const { compressImage } = await import('$lib/utils/image');

  const file = action.data.file;
  const onProgress = action.data.onProgress;

  // Compress image
  const compressed = await compressImage(file);

  // Convert blob to File
  const compressedFile = new File([compressed.blob], 'compressed.jpg', {
    type: 'image/jpeg',
    lastModified: Date.now()
  });

  // Upload compressed file
  const result = await receiptsService.upload({
    file: compressedFile,
    onProgress: (p) => {
      if (onProgress) onProgress((p * 0.8 + 20); // Add 20% for compression overhead
    }
  });

  // Store result
  const indexedDB = await getIndexedDB();
  await indexedDB.add('receipts', result.parsed_data);
}

async function processSplitCalculate(action: any): Promise<void> {
  console.log('[SW] Processing split calculation:', action);

  // Import calculation service
  const { calculateSplit } = await import('$lib/services/offline');

  const result = calculateSplit(
    action.data.people,
    action.data.items,
    action.data.assignments,
    action.data.tax,
    action.data.tip,
    action.data.split_evenly
  );

  // Store result
  const indexedDB = await getIndexedDB();
  await indexedDB.add('splits', result);
}
