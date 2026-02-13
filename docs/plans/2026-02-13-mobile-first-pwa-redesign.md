# Mobile-First PWA Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform Split-Bill from Streamlit to a modern mobile-first Progressive Web App with full offline capabilities, native-like UX, and production-grade performance.

**Architecture:** SvelteKit 5 + TypeScript frontend with Svelte 5 runes for reactive state, Vite for builds, vite-plugin-pwa for service worker/Background Sync. Existing FastAPI backend remains unchanged with async/Redis patterns preserved.

**Tech Stack:** Svelte 5, TypeScript 5.7+, SvelteKit 2.x, Vite 6.x, vite-plugin-pwa 0.21+, Tailwind CSS 4.x, Felte 2.x (forms), Skeleton UI 2.x

---

## Phase 1: Foundation Setup

### Task 1: Initialize SvelteKit Project

**Files:**
- Create: `web/package.json`
- Create: `web/svelte.config.js`
- Create: `web/vite.config.ts`
- Create: `web/tsconfig.json`
- Create: `web/.gitignore`

**Step 1: Create package.json**

Create `web/package.json`:

```json
{
  "name": "split-bill-web",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
    "check:watch": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json --watch",
    "test": "vitest",
    "test:ui": "vitest --ui"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^4.0.0",
    "@sveltejs/kit": "^2.8.0",
    "@sveltejs/adapter-static": "^3.0.0",
    "svelte": "^5.0.0",
    "typescript": "^5.7.2",
    "vite": "^6.0.0",
    "vitest": "^2.0.0"
  },
  "dependencies": {
    "vite-plugin-pwa": "^0.21.0"
  }
}
```

**Step 2: Create Svelte configuration**

Create `web/svelte.config.js`:

```javascript
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html',
      precompress: false,
      strict: true
    })
  }
};

export default config;
```

**Step 3: Create Vite configuration with PWA**

Create `web/vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    sveltekit(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'icon-192.png', 'icon-512.png'],
      manifest: {
        name: 'Split Bill',
        short_name: 'SplitBill',
        description: 'Split bills easily with friends',
        theme_color: '#000000',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any maskable'
          },
          {
            src: '/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ],
        categories: ['finance', 'productivity']
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/.*/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24
              }
            }
          }
        ],
        navigateFallback: '/offline'
      }
    })
  ]
});
```

**Step 4: Create TypeScript configuration**

Create `web/tsconfig.json`:

```json
{
  "extends": "./.svelte-kit/tsconfig.json",
  "compilerOptions": {
    "allowJs": true,
    "checkJs": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "sourceMap": true,
    "strict": true,
    "moduleResolution": "bundler"
  }
}
```

**Step 5: Create .gitignore**

Create `web/.gitignore`:

```
# Dependencies
node_modules/

# Build outputs
build/
.svelte-kit/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
.nyc_output/

# Misc
*.log
```

**Step 6: Commit**

```bash
cd web && git add .
git commit -m "feat: initialize SvelteKit project with PWA configuration"
```

---

### Task 2: Create Project Structure

**Files:**
- Create: `web/src/lib/components/ui/index.ts`
- Create: `web/src/lib/components/layout/index.ts`
- Create: `web/src/lib/components/features/receipt/index.ts`
- Create: `web/src/lib/components/features/split/index.ts`
- Create: `web/src/lib/components/features/share/index.ts`
- Create: `web/src/lib/stores/index.ts`
- Create: `web/src/lib/services/api/index.ts`
- Create: `web/src/lib/utils/index.ts`
- Create: `web/src/lib/types/index.ts`

**Step 1: Create directory structure**

```bash
mkdir -p web/src/lib/components/ui
mkdir -p web/src/lib/components/layout
mkdir -p web/src/lib/components/features/receipt
mkdir -p web/src/lib/components/features/split
mkdir -p web/src/lib/components/features/share
mkdir -p web/src/lib/stores
mkdir -p web/src/lib/services/api
mkdir -p web/src/lib/services/offline
mkdir -p web/src/lib/services/image
mkdir -p web/src/lib/services/notifications
mkdir -p web/src/lib/utils
mkdir -p web/src/lib/types
mkdir -p web/src/routes/(app)
mkdir -p web/src/routes/receipt
mkdir -p web/src/routes/split
mkdir -p web/src/routes/history
mkdir -p web/src/routes/settings
mkdir -p web/static
mkdir -p web/tests/unit
mkdir -p web/tests/integration
```

**Step 2: Create barrel exports**

Create `web/src/lib/components/ui/index.ts`:

```typescript
// UI components will be exported here
export {};
```

Create `web/src/lib/components/layout/index.ts`:

```typescript
// Layout components will be exported here
export {};
```

Create `web/src/lib/components/features/receipt/index.ts`:

```typescript
// Receipt feature components will be exported here
export {};
```

Create `web/src/lib/components/features/split/index.ts`:

```typescript
// Split feature components will be exported here
export {};
```

Create `web/src/lib/components/features/share/index.ts`:

```typescript
// Share feature components will be exported here
export {};
```

Create `web/src/lib/stores/index.ts`:

```typescript
// Stores will be exported here
export {};
```

Create `web/src/lib/services/api/index.ts`:

```typescript
// API services will be exported here
export {};
```

Create `web/src/lib/utils/index.ts`:

```typescript
// Utility functions will be exported here
export {};
```

Create `web/src/lib/types/index.ts`:

```typescript
// Type definitions will be exported here
export {};
```

**Step 3: Commit**

```bash
git add web/src/
git commit -m "feat: create project directory structure with barrel exports"
```

---

### Task 3: Add Tailwind CSS and Skeleton UI

**Files:**
- Create: `web/postcss.config.js`
- Create: `web/tailwind.config.js`
- Create: `web/src/app.css`
- Modify: `web/package.json`

**Step 1: Update package.json dependencies**

Modify `web/package.json`:

Add to `dependencies`:
```json
"@skeletonlabs/skeleton": "2.10.0",
"tailwindcss": "^4.0.0"
```

Add to `devDependencies`:
```json
"autoprefixer": "^10.4.0",
"postcss": "^8.4.0"
```

**Step 2: Create PostCSS configuration**

Create `web/postcss.config.js`:

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

**Step 3: Create Tailwind configuration**

Create `web/tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        }
      }
    }
  },
  plugins: [
    require('@skeletonlabs/skeleton/tailwind.cjs')({
      themes: ['skeleton', 'wintry', 'modern', 'crimson', 'gold-nouveau', 'vintage']
    })
  ]
};
```

**Step 4: Create global CSS**

Create `web/src/app.css`:

```css
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* Custom base styles */
:root {
  --color-primary: #0ea5e9;
  --color-primary-dark: #0284c7;
  --color-background: #ffffff;
  --color-surface: #f8fafc;
  --color-text: #0f172a;
  --color-text-secondary: #64748b;
}

/* Mobile-first base styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-family: system-ui, -apple-system, sans-serif;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  @apply bg-surface text-text;
  min-height: 100vh;
  min-height: 100dvh;
}

/* Touch-friendly tap targets */
button,
a,
[role="button"] {
  min-height: 44px;
  min-width: 44px;
}

/* Safe area insets for mobile */
.padding-safe {
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

.padding-safe-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Focus styles for accessibility */
:focus-visible {
  @apply outline-2 outline-offset-2 outline-primary-600;
}

/* Skip link for accessibility */
.skip-link {
  @apply sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4;
  @apply bg-primary-600 text-white px-4 py-2 rounded z-50;
}

/* Bottom navigation safe area */
.bottom-nav-safe {
  padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 0.75rem);
}
```

**Step 5: Install dependencies**

```bash
cd web && pnpm install
```

**Step 6: Commit**

```bash
git add web/
git commit -m "feat: add Tailwind CSS and Skeleton UI configuration"
```

---

### Task 4: Create API Client and Type Definitions

**Files:**
- Create: `web/src/lib/types/api.ts`
- Create: `web/src/lib/types/receipt.ts`
- Create: `web/src/lib/types/split.ts`
- Create: `web/src/lib/services/api/client.ts`

**Step 1: Create API type definitions**

Create `web/src/lib/types/api.ts`:

```typescript
/** API response wrapper */
export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

/** API error structure */
export interface ApiError {
  type: string;
  status_code: number;
  detail: string;
}

/** Receipt upload response */
export interface UploadReceiptResponse {
  parsed_data: ReceiptData;
  receipt_id: string;
}

/** Split calculation request */
export interface CalculateSplitRequest {
  person_names: string[];
  item_assignments: ItemAssignment[];
  tax_amount_input: number;
  tip_amount_input: number;
  split_evenly: boolean;
}

/** Split calculation response */
export interface CalculateSplitResponse {
  split_results: SplitResults;
  split_id: string;
}

/** Shared split data response */
export interface SharedSplitDataResponse {
  split_results: SplitResults;
  receipt_data: ReceiptData;
  created_at: string;
}

/** Health check response */
export interface HealthResponse {
  status: string;
  version: string;
}
```

**Step 2: Create receipt types**

Create `web/src/lib/types/receipt.ts`:

```typescript
/** Parsed receipt data from OCR */
export interface ReceiptData {
  items: ReceiptItem[];
  subtotal?: number;
  tax?: number;
  tip?: number;
  total?: number;
  merchant_name?: string;
  date?: string;
}

/** Individual receipt item */
export interface ReceiptItem {
  name: string;
  price: number;
  quantity?: number;
}

/** Item assignment for split */
export interface ItemAssignment {
  item_id: string;
  assigned_to: string[];
}
```

**Step 3: Create split types**

Create `web/src/lib/types/split.ts`:

```typescript
import type { ReceiptData } from './receipt';

/** Split calculation results */
export interface SplitResults {
  [personName: string]: PersonSplit;
}

/** Individual person's split */
export interface PersonSplit {
  total: number;
  items: AssignedItem[];
  tax_share: number;
  tip_share: number;
}

/** Item assigned to a person */
export interface AssignedItem {
  name: string;
  price: number;
  quantity: number;
}

/** Split state for store */
export interface SplitState {
  people: string[];
  items: ReceiptItem[];
  assignments: ItemAssignment[];
  tax: number;
  tip: number;
  split_evenly: boolean;
  results: SplitResults | null;
  loading: boolean;
  error: string | null;
}
```

**Step 4: Create API client base class**

Create `web/src/lib/services/api/client.ts`:

```typescript
import type {
  ApiResponse,
  ApiError,
  UploadReceiptResponse,
  CalculateSplitRequest,
  CalculateSplitResponse,
  SharedSplitDataResponse,
  HealthResponse
} from '$lib/types/api';

interface ApiConfig {
  baseURL: string;
  apiKey: string;
  timeout: number;
}

/** Custom API error class */
export class ApiError extends Error {
  constructor(
    public message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Type-safe API client */
export class ApiClient {
  private config: ApiConfig;

  constructor(config: ApiConfig) {
    this.config = config;
  }

  /** Make authenticated API request */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.config.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`,
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new ApiError(
          error.error?.detail || 'Request failed',
          response.status,
          error
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408);
      }
      throw new ApiError('Network error', 0);
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async postForm<T>(endpoint: string, formData: FormData): Promise<T> {
    const url = `${this.config.baseURL}${endpoint}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        error.error?.detail || 'Upload failed',
        response.status,
        error
      );
    }

    return response.json();
  }
}

/** Singleton instance */
let apiClientInstance: ApiClient | null = null;

/** Initialize API client with configuration */
export function initApiClient(config: ApiConfig): ApiClient {
  apiClientInstance = new ApiClient(config);
  return apiClientInstance;
}

/** Get initialized API client */
export function getApiClient(): ApiClient {
  if (!apiClientInstance) {
    throw new Error('API client not initialized. Call initApiClient first.');
  }
  return apiClientInstance;
}
```

**Step 5: Update types barrel export**

Modify `web/src/lib/types/index.ts`:

```typescript
export * from './api';
export * from './receipt';
export * from './split';
```

**Step 6: Commit**

```bash
git add web/src/lib/types web/src/lib/services/api/
git commit -m "feat: add API type definitions and base client"
```

---

### Task 5: Create API Endpoint Services

**Files:**
- Create: `web/src/lib/services/api/receipts.ts`
- Create: `web/src/lib/services/api/splits.ts`
- Create: `web/src/lib/services/api/health.ts`
- Modify: `web/src/lib/services/api/index.ts`

**Step 1: Create receipts service**

Create `web/src/lib/services/api/receipts.ts`:

```typescript
import { getApiClient } from './client';
import type { UploadReceiptResponse } from '$lib/types/api';

export interface UploadReceiptOptions {
  file: File;
  onProgress?: (progress: number) => void;
}

/** Receipt upload and OCR service */
export class ReceiptsService {
  /** Upload receipt for OCR processing */
  async upload(options: UploadReceiptOptions): Promise<UploadReceiptResponse> {
    const apiClient = getApiClient();
    const formData = new FormData();
    formData.append('file', options.file);

    // For large files, use XMLHttpRequest for progress tracking
    if (options.onProgress && options.file.size > 1024 * 1024) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            options.onProgress!(progress);
          }
        });

        xhr.addEventListener('load', () => {
          if (xhr.status === 200) {
            resolve(JSON.parse(xhr.responseText));
          } else {
            reject(new Error(xhr.responseText));
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Upload failed'));
        });

        xhr.open('POST', `${apiClient['config'].baseURL}/receipts/upload`);
        xhr.setRequestHeader('Authorization', `Bearer ${apiClient['config'].apiKey}`);
        xhr.send(formData);
      });
    }

    return apiClient.postForm<UploadReceiptResponse>('/receipts/upload', formData);
  }

  /** Validate image before upload */
  validateImage(file: File): { valid: boolean; error?: string } {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const maxSize = 2 * 1024 * 1024; // 2MB

    if (!validTypes.includes(file.type)) {
      return { valid: false, error: 'Invalid file type. Please upload JPEG, PNG, or WebP.' };
    }

    if (file.size > maxSize) {
      return { valid: false, error: `File too large. Maximum size is 2MB.` };
    }

    return { valid: true };
  }
}

export const receiptsService = new ReceiptsService();
```

**Step 2: Create splits service**

Create `web/src/lib/services/api/splits.ts`:

```typescript
import { getApiClient } from './client';
import type {
  CalculateSplitRequest,
  CalculateSplitResponse,
  SharedSplitDataResponse
} from '$lib/types/api';

/** Split calculation service */
export class SplitsService {
  /** Calculate bill split */
  async calculate(request: CalculateSplitRequest): Promise<CalculateSplitResponse> {
    const apiClient = getApiClient();
    return apiClient.post<CalculateSplitResponse>('/splits/calculate', request);
  }

  /** Get shared split data */
  async getShared(splitId: string): Promise<SharedSplitDataResponse> {
    const apiClient = getApiClient();
    return apiClient.get<SharedSplitDataResponse>(`/splits/view/${splitId}`);
  }
}

export const splitsService = new SplitsService();
```

**Step 3: Create health service**

Create `web/src/lib/services/api/health.ts`:

```typescript
import { getApiClient } from './client';
import type { HealthResponse } from '$lib/types/api';

/** Health check service */
export class HealthService {
  /** Check API health */
  async check(): Promise<HealthResponse> {
    const apiClient = getApiClient();
    return apiClient.get<HealthResponse>('/health');
  }
}

export const healthService = new HealthService();
```

**Step 4: Update API services barrel export**

Modify `web/src/lib/services/api/index.ts`:

```typescript
export * from './client';
export * from './receipts';
export * from './splits';
export * from './health';
```

**Step 5: Commit**

```bash
git add web/src/lib/services/api/
git commit -m "feat: add API endpoint services (receipts, splits, health)"
```

---

### Task 6: Create Svelte Stores for State Management

**Files:**
- Create: `web/src/lib/stores/offline.ts`
- Create: `web/src/lib/stores/receipt.ts`
- Create: `web/src/lib/stores/split.ts`

**Step 1: Create offline store**

Create `web/src/lib/stores/offline.ts`:

```typescript
import { writable, derived } from 'svelte/store';

interface OfflineState {
  online: boolean;
  since: Date | null;
  queuedActions: number;
}

function createOfflineStore() {
  const { subscribe, set, update } = writable<OfflineState>({
    online: typeof navigator !== 'undefined' ? navigator.onLine : true,
    since: null,
    queuedActions: 0,
  });

  // Listen for online/offline events
  if (typeof window !== 'undefined') {
    window.addEventListener('online', () => {
      update(s => ({ ...s, online: true, since: null }));
    });

    window.addEventListener('offline', () => {
      update(s => ({ ...s, online: false, since: new Date() }));
    });
  }

  return {
    subscribe,
    get online() { return typeof navigator !== 'undefined' ? navigator.onLine : true; },
    incrementQueued: () => update(s => ({ ...s, queuedActions: s.queuedActions + 1 })),
    decrementQueued: () => update(s => ({ ...s, queuedActions: Math.max(0, s.queuedActions - 1) })),
  };
}

export const offlineStore = createOfflineStore();

// Derived stores
export const isOffline = derived(offlineStore, $offline => !$offline.online);
export const hasQueuedActions = derived(offlineStore, $offline => $offline.queuedActions > 0);
```

**Step 2: Create receipt store**

Create `web/src/lib/stores/receipt.ts`:

```typescript
import { writable } from 'svelte/store';
import type { ReceiptData } from '$lib/types/receipt';

interface ReceiptState {
  currentReceipt: ReceiptData | null;
  loading: boolean;
  error: string | null;
}

function createReceiptStore() {
  const { subscribe, set, update } = writable<ReceiptState>({
    currentReceipt: null,
    loading: false,
    error: null,
  });

  return {
    subscribe,
    get currentReceipt() { return null; }, // Will be updated by Svelte 5 runes
    setReceipt: (data: ReceiptData) => update(s => ({ ...s, currentReceipt: data, error: null })),
    clearReceipt: () => update(s => ({ ...s, currentReceipt: null, error: null })),
    setLoading: (loading: boolean) => update(s => ({ ...s, loading })),
    setError: (error: string | null) => update(s => ({ ...s, error })),
  };
}

export const receiptStore = createReceiptStore();
```

**Step 3: Create split store**

Create `web/src/lib/stores/split.ts`:

```typescript
import { writable } from 'svelte/store';
import type { SplitState, SplitResults } from '$lib/types/split';
import type { ReceiptData } from '$lib/types/receipt';

function createSplitStore() {
  const { subscribe, set, update } = writable<SplitState>({
    people: ['Person 1', 'Person 2'],
    items: [],
    assignments: [],
    tax: 0,
    tip: 0,
    split_evenly: false,
    results: null,
    loading: false,
    error: null,
  });

  return {
    subscribe,
    setPeople: (people: string[]) => update(s => ({ ...s, people })),
    setItems: (items: ReceiptData['items']) => update(s => ({ ...s, items })),
    setTax: (tax: number) => update(s => ({ ...s, tax })),
    setTip: (tip: number) => update(s => ({ ...s, tip })),
    setSplitEvenly: (split_evenly: boolean) => update(s => ({ ...s, split_evenly })),
    setResults: (results: SplitResults) => update(s => ({ ...s, results })),
    setLoading: (loading: boolean) => update(s => ({ ...s, loading })),
    setError: (error: string | null) => update(s => ({ ...s, error })),
    reset: () => update(s => ({
      people: ['Person 1', 'Person 2'],
      items: [],
      assignments: [],
      tax: 0,
      tip: 0,
      split_evenly: false,
      results: null,
      loading: false,
      error: null,
    })),
  };
}

export const splitStore = createSplitStore();
```

**Step 4: Update stores barrel export**

Modify `web/src/lib/stores/index.ts`:

```typescript
export * from './offline';
export * from './receipt';
export * from './split';
```

**Step 5: Commit**

```bash
git add web/src/lib/stores/
git commit -m "feat: add Svelte stores for state management"
```

---

### Task 7: Create Basic UI Components

**Files:**
- Create: `web/src/lib/components/ui/Button.svelte`
- Create: `web/src/lib/components/ui/Input.svelte`
- Create: `web/src/lib/components/ui/Card.svelte`
- Create: `web/src/lib/components/ui/Progress.svelte`

**Step 1: Create Button component**

Create `web/src/lib/components/ui/Button.svelte`:

```svelte
<script lang="ts">
  import type { Snippet } from '@sveltejs/kit';

  interface Props {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
    class?: string;
    children?: Snippet;
    onclick?: (event: MouseEvent) => void;
  }

  const {
    variant = 'primary',
    size = 'md',
    disabled = false,
    type = 'button',
    class: className = '',
    children,
    onclick
  }: Props = $props();

  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:outline-primary-600',
    secondary: 'bg-surface-200 text-text hover:bg-surface-300 focus-visible:outline-primary-600',
    ghost: 'bg-transparent text-text hover:bg-surface-100 focus-visible:outline-primary-600',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus-visible:outline-red-600',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm min-h-[36px]',
    md: 'px-4 py-2 text-base min-h-[44px]',
    lg: 'px-6 py-3 text-lg min-h-[52px]',
  };
</script>

<button
  {type}
  class="{baseClasses} {variantClasses[variant]} {sizeClasses[size]} {className}"
  {disabled}
  on:click={onclick}
>
  {#if children}
    {@render children()}
  {:else}
    <slot />
  {/if}
</button>
```

**Step 2: Create Input component**

Create `web/src/lib/components/ui/Input.svelte`:

```svelte
<script lang="ts">
  interface Props {
    type?: 'text' | 'email' | 'tel' | 'number';
    value?: string;
    placeholder?: string;
    disabled?: boolean;
    required?: boolean;
    class?: string;
    oninput?: (value: string) => void;
    onchange?: (value: string) => void;
  }

  const {
    type = 'text',
    value = '',
    placeholder = '',
    disabled = false,
    required = false,
    class: className = '',
    oninput,
    onchange,
  }: Props = $props();

  let inputValue = $state(value);
</script>

<div class="relative">
  <input
    {type}
    {placeholder}
    {disabled}
    {required}
    bind:value={inputValue}
    oninput={(e) => {
      if (oninput) oninput(e.currentTarget.value);
      if (onchange) onchange(e.currentTarget.value);
    }}
    class="w-full px-4 py-3 text-base bg-white border border-surface-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none disabled:bg-surface-100 disabled:cursor-not-allowed min-h-[44px] {className}"
  />
</div>
```

**Step 3: Create Card component**

Create `web/src/lib/components/ui/Card.svelte`:

```svelte
<script lang="ts">
  interface Props {
    padding?: 'none' | 'sm' | 'md' | 'lg';
    class?: string;
  }

  const { padding = 'md', class: className = '' }: Props = $props();

  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
</script>

<div class="bg-white rounded-xl shadow-sm border border-surface-200 {paddingClasses[padding]} {className}">
  <slot />
</div>
```

**Step 4: Create Progress component**

Create `web/src/lib/components/ui/Progress.svelte`:

```svelte
<script lang="ts">
  interface Props {
    value: number; // 0-100
    max?: number;
    class?: string;
  }

  const { value, max = 100, class: className = '' }: Props = $props();

  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
</script>

<div class="w-full bg-surface-200 rounded-full overflow-hidden {className}" role="progressbar" aria-valuenow={value} aria-valuemax={max}>
  <div
    class="h-full bg-primary-600 transition-all duration-300 ease-out"
    style="width: {percentage}%"
  />
</div>
```

**Step 5: Update UI components barrel export**

Modify `web/src/lib/components/ui/index.ts`:

```typescript
export { default as Button } from './Button.svelte';
export { default as Input } from './Input.svelte';
export { default as Card } from './Card.svelte';
export { default as Progress } from './Progress.svelte';
```

**Step 6: Commit**

```bash
git add web/src/lib/components/ui/
git commit -m "feat: add base UI components (Button, Input, Card, Progress)"
```

---

### Task 8: Create Layout Components

**Files:**
- Create: `web/src/lib/components/layout/OfflineBanner.svelte`
- Create: `web/src/lib/components/layout/BottomNav.svelte`
- Create: `web/src/lib/components/layout/AppShell.svelte`
- Modify: `web/src/lib/components/layout/index.ts`

**Step 1: Create OfflineBanner component**

Create `web/src/lib/components/layout/OfflineBanner.svelte`:

```svelte
<script lang="ts">
  import { isOffline, hasQueuedActions } from '$lib/stores/offline';
  import { offlineStore } from '$lib/stores/offline';
</script>

{#if $isOffline}
<div class="fixed top-0 left-0 right-0 z-50 bg-yellow-100 text-yellow-800 px-4 py-3 flex items-center gap-3 shadow-md" role="alert">
  <span class="text-xl" aria-hidden="true">📡</span>
  <span class="flex-1 text-sm font-medium">
    You're offline. Actions will be synced when connection returns.
  </span>
  {#if $hasQueuedActions}
    <span class="px-2 py-1 bg-red-600 text-white text-xs font-semibold rounded-full">
      {$offlineStore.queuedActions} pending
    </span>
  {/if}
</div>
{/if}
```

**Step 2: Create BottomNav component**

Create `web/src/lib/components/layout/BottomNav.svelte`:

```svelte
<script lang="ts">
  import type { Snippet } from '@sveltejs/kit';

  interface NavItem {
    path: string;
    icon: string;
    label: string;
  }

  interface Props {
    currentPath: string;
    class?: string;
  }

  const { currentPath, class: className = '' }: Props = $props();

  const navItems: NavItem[] = [
    { path: '/', icon: '🏠', label: 'Home' },
    { path: '/receipt', icon: '📸', label: 'Receipt' },
    { path: '/split', icon: '💰', label: 'Split' },
    { path: '/history', icon: '📋', label: 'History' },
  ];
</script>

<nav
  class="fixed bottom-0 left-0 right-0 bg-white border-t border-surface-200 z-40 bottom-nav-safe {className}"
  role="navigation"
  aria-label="Main navigation"
>
  <ul class="flex items-center justify-around">
    {#each navItems as item}
      <li>
        <a
          href={item.path}
          class="flex flex-col items-center justify-center flex-1 min-h-[60px] text-center transition-colors {currentPath === item.path ? 'text-primary-600' : 'text-text-secondary hover:text-primary-600'}"
          aria-current={currentPath === item.path ? 'page' : undefined}
        >
          <span class="text-2xl mb-1" aria-hidden="true">{item.icon}</span>
          <span class="text-xs font-medium">{item.label}</span>
        </a>
      </li>
    {/each}
  </ul>
</nav>
```

**Step 3: Create AppShell component**

Create `web/src/lib/components/layout/AppShell.svelte`:

```svelte
<script lang="ts">
  import type { Snippet } from '@sveltejs/kit';

  interface Props {
    title?: string;
    class?: string;
    children?: Snippet;
  }

  const { title = 'Split Bill', class: className = '', children }: Props = $props();
</script>

<div class="flex flex-col min-h-screen bg-surface pb-[60px]">
  <!-- Header -->
  <header class="sticky top-0 z-30 bg-white border-b border-surface-200 px-4 py-3">
    <h1 class="text-xl font-semibold text-text">{title}</h1>
  </header>

  <!-- Main Content -->
  <main class="flex-1 px-4 py-4 {className}">
    {#if children}
      {@render children()}
    {:else}
      <slot />
    {/if}
  </main>
</div>
```

**Step 4: Update layout components barrel export**

Modify `web/src/lib/components/layout/index.ts`:

```typescript
export { default as OfflineBanner } from './OfflineBanner.svelte';
export { default as BottomNav } from './BottomNav.svelte';
export { default as AppShell } from './AppShell.svelte';
```

**Step 5: Commit**

```bash
git add web/src/lib/components/layout/
git commit -m "feat: add layout components (OfflineBanner, BottomNav, AppShell)"
```

---

### Task 9: Create Main App Layout and Pages

**Files:**
- Create: `web/src/app.html`
- Create: `web/src/app.css`
- Create: `web/src/routes/(app)/+layout.svelte`
- Create: `web/src/routes/(app)/+page.svelte`
- Create: `web/src/routes/+layout.server.ts` (API client initialization)
- Create: `web/src/routes/+error.svelte`

**Step 1: Create app.html template**

Create `web/src/app.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%sveltekit.assets%/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="description" content="Split bills easily with friends" />
    <meta name="theme-color" content="#000000" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
    %sveltekit.head%
  </head>
  <body data-sveltekit-preload-data="hover">
    %sveltekit.body%
    <noscript>
      <div style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: system-ui;">
        <div style="text-align: center;">
          <h1>JavaScript Required</h1>
          <p>This app requires JavaScript to function.</p>
        </div>
      </div>
    </noscript>
  </body>
</html>
```

**Step 2: Create app.css (ensure it references the CSS file)**

Create `web/src/app.css` (update if already exists):

```css
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* Add custom styles from Task 3 if not already present */
```

**Step 3: Create root layout**

Create `web/src/routes/+layout.server.ts`:

```typescript
import { initApiClient } from '$lib/services/api';
import type { RequestHandler } from '@sveltejs/kit';

export const load: RequestHandler = async () => {
  // Initialize API client from environment variables
  const apiConfig = {
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    apiKey: import.meta.env.VITE_API_KEY || '',
    timeout: 30000,
  };

  initApiClient(apiConfig);

  return {};
};
```

**Step 4: Create app group layout**

Create `web/src/routes/(app)/+layout.svelte`:

```svelte
<script lang="ts">
  import AppShell from '$lib/components/layout/AppShell.svelte';
  import OfflineBanner from '$lib/components/layout/OfflineBanner.svelte';
  import BottomNav from '$lib/components/layout/BottomNav.svelte';
  import { page } from '$app/stores';

  let currentPath = $state(page.url.pathname);
  $effect(() => {
    currentPath = page.url.pathname;
  });
</script>

<OfflineBanner />
<AppShell>
  <slot />
</AppShell>
<BottomNav currentPath={currentPath} />
```

**Step 5: Create home page**

Create `web/src/routes/(app)/+page.svelte`:

```svelte
<script lang="ts">
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
</script>

<svelte:head>
  <title>Split Bill - Home</title>
</svelte:head>

<div class="space-y-4">
  <Card>
    <h2 class="text-lg font-semibold mb-2">Welcome to Split Bill</h2>
    <p class="text-text-secondary">Split bills easily with friends using your phone.</p>
  </Card>

  <div class="grid grid-cols-2 gap-4">
    <a href="/receipt">
      <Card class="text-center hover:bg-surface-50 transition-colors cursor-pointer">
        <div class="text-4xl mb-2" aria-hidden="true">📸</div>
        <h3 class="font-semibold">Upload Receipt</h3>
        <p class="text-sm text-text-secondary">Scan or upload</p>
      </Card>
    </a>

    <a href="/split">
      <Card class="text-center hover:bg-surface-50 transition-colors cursor-pointer">
        <div class="text-4xl mb-2" aria-hidden="true">💰</div>
        <h3 class="font-semibold">New Split</h3>
        <p class="text-sm text-text-secondary">Create a split</p>
      </Card>
    </a>
  </div>
</div>
```

**Step 6: Create error page**

Create `web/src/routes/+error.svelte`:

```svelte
<script lang="ts">
  import type { LoadEvent } from '@sveltejs/kit';
  import Button from '$lib/components/ui/Button.svelte';

  interface Props {
    data: LoadEvent['data'];
    form?: LoadEvent['form'];
    status: number;
    error: Error & { message: string; };
  }

  const { status, error }: Props = $props();
</script>

<svelte:head>
  <title>Error {status} - Split Bill</title>
</svelte:head>

<Card>
  <div class="text-center py-8">
    <div class="text-6xl mb-4" aria-hidden="true">⚠️</div>
    <h1 class="text-2xl font-bold mb-2">Error {status}</h1>
    <p class="text-text-secondary mb-6">{error.message}</p>
    <Button onclick={() => window.history.back()}>Go Back</Button>
  </div>
</Card>
```

**Step 7: Commit**

```bash
git add web/src/app.html web/src/app.css web/src/routes/
git commit -m "feat: create main app layout and home page"
```

---

## Phase 2: Core Features

### Task 10: Create Receipt Upload Page

**Files:**
- Create: `web/src/routes/receipt/+page.svelte`
- Create: `web/src/lib/components/features/receipt/UploadZone.svelte`

**Step 1: Create UploadZone component**

Create `web/src/lib/components/features/receipt/UploadZone.svelte`:

```svelte
<script lang="ts">
  import type { Snippet } from '@sveltejs/kit';
  import { receiptsService } from '$lib/services/api';
  import { receiptStore } from '$lib/stores/receipt';
  import { offlineStore } from '$lib/stores/offline';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Progress from '$lib/components/ui/Progress.svelte';

  interface Props {
    onUploadComplete?: (data: import('$lib/types/api').UploadReceiptResponse) => void;
  }

  const { onUploadComplete }: Props = $props();

  let files = $state<FileList | null>(null);
  let uploading = $state(false);
  let progress = $state(0);
  let error = $state<string | null>(null);
  let dragActive = $state(false);

  async function handleUpload() {
    if (!files || files.length === 0) return;

    const file = files[0];

    // Validate
    const validation = receiptsService.validateImage(file);
    if (!validation.valid) {
      error = validation.error || 'Invalid file';
      return;
    }

    error = null;
    uploading = true;
    progress = 0;

    try {
      // Check if offline
      if (!offlineStore.online) {
        error = 'You\'re offline. Receipt will be uploaded when you reconnect.';
        // TODO: Queue for background sync (Phase 3)
        return;
      }

      // Upload with progress
      const result = await receiptsService.upload({
        file,
        onProgress: (p) => { progress = p; }
      });

      // Update store
      receiptStore.setReceipt(result.parsed_data);

      if (onUploadComplete) {
        onUploadComplete(result);
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Upload failed';
    } finally {
      uploading = false;
      progress = 0;
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragActive = true;
  }

  function handleDragLeave(e: DragEvent) {
    e.preventDefault();
    dragActive = false;
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragActive = false;
    if (e.dataTransfer?.files) {
      files = e.dataTransfer.files;
    }
  }
</script>

<Card
  class="relative"
  class:drag-active={dragActive}
  ondragover={handleDragOver}
  ondragleave={handleDragLeave}
  ondrop={handleDrop}
>
  <div class="space-y-4">
    <!-- Upload Area -->
    <div class="border-2 border-dashed border-surface-300 rounded-lg p-8 text-center {dragActive ? 'border-primary-500 bg-primary-50' : ''}">
      <div class="text-5xl mb-4" aria-hidden="true">📸</div>
      <p class="font-medium mb-2">
        {#if uploading}
          Uploading receipt...
        {:else}
          Drop receipt image here or tap to browse
        {/if}
      </p>
      <input
        type="file"
        accept="image/*"
        bind:files
        disabled={uploading}
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        aria-label="Upload receipt image"
      />
    </div>

    <!-- Progress Bar -->
    {#if uploading}
      <div class="space-y-2">
        <div class="flex justify-between text-sm">
          <span>Uploading...</span>
          <span>{progress}%</span>
        </div>
        <Progress value={progress} />
      </div>
    {/if}

    <!-- Error Message -->
    {#if error}
      <div class="bg-red-50 text-red-800 px-4 py-3 rounded-lg" role="alert">
        {error}
      </div>
    {/if}

    <!-- Upload Button -->
    <Button
      variant="primary"
      disabled={uploading || !files || files.length === 0}
      onclick={handleUpload}
    >
      {uploading ? 'Uploading...' : 'Upload Receipt'}
    </Button>
  </div>
</Card>

<style>
  .drag-active {
    @apply border-primary-500;
  }
</style>
```

**Step 2: Create receipt page**

Create `web/src/routes/receipt/+page.svelte`:

```svelte
<script lang="ts">
  import UploadZone from '$lib/components/features/receipt/UploadZone.svelte';

  function handleUploadComplete(data: import('$lib/types/api').UploadReceiptResponse) {
    // Navigate to split page with receipt data
    window.location.href = `/split?receiptId=${data.receipt_id}`;
  }
</script>

<svelte:head>
  <title>Upload Receipt - Split Bill</title>
</svelte:head>

<UploadZone onUploadComplete={handleUploadComplete} />
```

**Step 3: Update receipt components barrel export**

Modify `web/src/lib/components/features/receipt/index.ts`:

```typescript
export { default as UploadZone } from './UploadZone.svelte';
```

**Step 4: Commit**

```bash
git add web/src/routes/receipt/ web/src/lib/components/features/receipt/
git commit -m "feat: add receipt upload page and component"
```

---

### Task 11: Create Split Calculation Page

**Files:**
- Create: `web/src/routes/split/+page.svelte`
- Create: `web/src/lib/components/features/split/PersonManager.svelte`
- Create: `web/src/lib/components/features/split/SplitResults.svelte`

**Step 1: Create PersonManager component**

Create `web/src/lib/components/features/split/PersonManager.svelte`:

```svelte
<script lang="ts">
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import { splitStore } from '$lib/stores/split';

  interface Props {
    people: string[];
    onUpdate: (people: string[]) => void;
  }

  const { people, onUpdate }: Props = $props();

  let newPersonName = $state('');

  function addPerson() {
    if (newPersonName.trim()) {
      onUpdate([...people, newPersonName.trim()]);
      newPersonName = '';
    }
  }

  function removePerson(index: number) {
    const updated = people.filter((_, i) => i !== index);
    onUpdate(updated);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      addPerson();
    }
  }
</script>

<Card>
  <div class="space-y-4">
    <h2 class="font-semibold">People ({people.length})</h2>

    <!-- Add Person Input -->
    <div class="flex gap-2">
      <Input
        bind:value={newPersonName}
        placeholder="Add person..."
        onkeydown={handleKeydown}
        class="flex-1"
      />
      <Button variant="primary" onclick={addPerson} disabled={!newPersonName.trim()}>
        Add
      </Button>
    </div>

    <!-- People List -->
    <div class="space-y-2">
      {#each people as person, index}
        <div class="flex items-center gap-2 p-2 bg-surface-50 rounded-lg">
          <span class="flex-1 font-medium">{person}</span>
          <button
            onclick={() => removePerson(index)}
            class="text-red-600 hover:text-red-700 p-2"
            aria-label="Remove {person}"
          >
            ✕
          </button>
        </div>
      {/each}
    </div>
  </div>
</Card>
```

**Step 2: Create SplitResults component**

Create `web/src/lib/components/features/split/SplitResults.svelte`:

```svelte
<script lang="ts">
  import type { SplitResults } from '$lib/types/split';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  interface Props {
    results: SplitResults;
    splitId?: string;
  }

  const { results, splitId }: Props = $props();

  const shareUrl = splitId ? `${window.location.origin}/split/${splitId}` : window.location.href;

  async function copyShareLink() {
    await navigator.clipboard.writeText(shareUrl);
    // TODO: Show toast notification
  }

  const totalAmount = Object.values(results).reduce((sum, r) => sum + r.total, 0);
</script>

<Card>
  <div class="space-y-4">
    <h2 class="text-lg font-semibold">Split Results</h2>

    <div class="text-center p-4 bg-primary-50 rounded-lg">
      <p class="text-sm text-primary-700">Total</p>
      <p class="text-3xl font-bold text-primary-700">${totalAmount.toFixed(2)}</p>
    </div>

    <!-- Per-Person Breakdown -->
    <div class="space-y-2">
      {#each Object.entries(results) as [name, data]}
        <div class="p-3 bg-surface-50 rounded-lg">
          <div class="flex justify-between items-center mb-2">
            <h3 class="font-semibold">{name}</h3>
            <span class="text-lg font-bold">${data.total.toFixed(2)}</span>
          </div>
          <p class="text-sm text-text-secondary">
            {data.items.length} items · Tax: ${data.tax_share.toFixed(2)} · Tip: ${data.tip_share.toFixed(2)}
          </p>
        </div>
      {/each}
    </div>

    <!-- Share Actions -->
    <div class="flex gap-2">
      <Button variant="primary" onclick={copyShareLink} class="flex-1">
        📋 Copy Link
      </Button>
    </div>
  </div>
</Card>
```

**Step 3: Create split page**

Create `web/src/routes/split/+page.svelte`:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { splitsService } from '$lib/services/api';
  import { splitStore } from '$lib/stores/split';
  import { receiptStore } from '$lib/stores/receipt';
  import PersonManager from '$lib/components/features/split/PersonManager.svelte';
  import SplitResults from '$lib/components/features/split/SplitResults.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Progress from '$lib/components/ui/Progress.svelte';

  let people = $state<string[]>(['Person 1', 'Person 2']);
  let tax = $state(0);
  let tip = $state(0);
  let calculating = $state(false);

  function handleCalculateSplit() {
    calculating = true;
    const receiptData = receiptStore.currentReceipt;

    if (!receiptData || !receiptData.items.length) {
      alert('Please upload a receipt first');
      calculating = false;
      return;
    }

    // Create assignments (each item assigned to all people by default)
    const assignments = receiptData.items.map(item => ({
      item_id: item.name,
      assigned_to: people,
    }));

    const request = {
      person_names: people,
      item_assignments: assignments,
      tax_amount_input: tax,
      tip_amount_input: tip,
      split_evenly: false,
    };

    splitsService.calculate(request)
      .then(response => {
        splitStore.setResults(response.split_results);
        splitStore.setPeople(people);
        splitStore.setItems(receiptData.items);
      })
      .catch(error => {
        alert(`Failed to calculate split: ${error.message}`);
      })
      .finally(() => {
        calculating = false;
      });
  }

  function resetSplit() {
    people = ['Person 1', 'Person 2'];
    tax = 0;
    tip = 0;
    splitStore.reset();
  }
</script>

<svelte:head>
  <title>Create Split - Split Bill</title>
</svelte:head>

<div class="space-y-4">
  <!-- Person Manager -->
  <PersonManager people={people} onUpdate={(p) => people = p} />

  <!-- Tax & Tip -->
  <Card>
    <div class="space-y-4">
      <h2 class="font-semibold">Tax & Tip</h2>

      <div>
        <label for="tax-input" class="block text-sm font-medium mb-1">Tax</label>
        <input
          id="tax-input"
          type="number"
          bind:value={tax}
          step="0.01"
          min="0"
          class="w-full px-4 py-3 text-base bg-white border border-surface-300 rounded-lg min-h-[44px]"
          placeholder="0.00"
        />
      </div>

      <div>
        <label for="tip-input" class="block text-sm font-medium mb-1">Tip</label>
        <input
          id="tip-input"
          type="number"
          bind:value={tip}
          step="0.01"
          min="0"
          class="w-full px-4 py-3 text-base bg-white border border-surface-300 rounded-lg min-h-[44px]"
          placeholder="0.00"
        />
      </div>
    </div>
  </Card>

  <!-- Actions -->
  <div class="flex gap-2">
    <Button
      variant="primary"
      onclick={handleCalculateSplit}
      disabled={calculating}
      class="flex-1"
    >
      {calculating ? 'Calculating...' : 'Calculate Split'}
    </Button>
    <Button
      variant="ghost"
      onclick={resetSplit}
      disabled={calculating}
    >
      Reset
    </Button>
  </div>

  <!-- Results -->
  {#if splitStore.results}
    <SplitResults results={splitStore.results} />
  {/if}
</div>
```

**Step 4: Update split components barrel export**

Modify `web/src/lib/components/features/split/index.ts`:

```typescript
export { default as PersonManager } from './PersonManager.svelte';
export { default as SplitResults } from './SplitResults.svelte';
```

**Step 5: Commit**

```bash
git add web/src/routes/split/ web/src/lib/components/features/split/
git commit -m "feat: add split calculation page and components"
```

---

## Verification Steps

After completing all tasks:

### 1. Install Dependencies
```bash
cd web && pnpm install
```

### 2. Set Environment Variables
Create `web/.env`:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=your-api-key-here
```

### 3. Start Development Server
```bash
cd web && pnpm dev
```

### 4. Test Core Functionality
- [ ] Navigate to http://localhost:5173
- [ ] Verify home page loads with quick action cards
- [ ] Navigate to `/receipt` and test file upload
- [ ] Navigate to `/split` and verify person manager works
- [ ] Test tax/tip inputs
- [ ] Calculate split and verify results display
- [ ] Test offline banner (disconnect network)

### 5. Build for Production
```bash
cd web && pnpm build
```

### 6. Verify PWA Features
- [ ] Check build contains `manifest.webmanifest`
- [ ] Check build contains `service-worker.js`
- [ ] Test PWA install prompt (Chrome DevTools > Application > PWA)
- [ ] Verify service worker caching strategies

---

## Summary

This plan implements Phase 1 (Foundation) and Phase 2 (Core Features) of the mobile-first PWA redesign. Key deliverables:

1. **Foundation:**
   - SvelteKit 5 + TypeScript project structure
   - Tailwind CSS + Skeleton UI configuration
   - PWA configuration with service worker strategies
   - Type-safe API client with idempotency support

2. **Core Features:**
   - Receipt upload with OCR integration
   - Split calculation UI
   - Offline detection and indicators
   - Mobile-first navigation (bottom tab bar)

3. **Performance:**
   - Route-based code splitting (automatic)
   - Optimized bundle targets (< 200KB initial)
   - Touch-friendly components (44x44px minimum)

**Next phases** (not in this plan):
- Phase 3: Offline-First (Background Sync, IndexedDB queue)
- Phase 4: Polish & Performance (optimization, testing)
- Phase 5: Advanced Features (WebAuthn, feature flags)
