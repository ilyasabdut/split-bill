# Page Dependency Trees

Complete dependency trees for the main routes in Split Bill.

## Home Page (src/routes/(app)/+page.svelte)
- `src/lib/components/ui/Card.svelte`
- `src/lib/components/ui/Button.svelte`

## Receipt Upload Page (src/routes/receipt/+page.svelte)
- `src/lib/components/features/receipt/UploadZone.svelte`
- `src/lib/stores/receipt.ts`
- `src/lib/types/api.ts`

## Create Split Page (src/routes/split/+page.svelte)
- `src/lib/components/features/split/PersonManager.svelte`
- `src/lib/components/features/split/SplitResults.svelte`
- `src/lib/components/ui/Card.svelte`
- `src/lib/components/ui/Button.svelte`
- `src/lib/services/api/index.ts`
- `src/lib/stores/index.ts`
- `src/lib/services/offline/index.ts`
- `src/lib/stores/offline.ts`

## History Page (src/routes/history/+page.svelte)
- `src/lib/components/ui/Card.svelte`
- `src/lib/components/ui/Button.svelte`
- `src/lib/services/offline/indexeddb.ts`
- `src/lib/types/split.ts`

## Settings Page (src/routes/settings/+page.svelte)
- `src/lib/components/ui/Card.svelte`
- `src/lib/components/ui/Button.svelte`
- `src/lib/stores/offline.ts`
- `src/lib/services/offline/indexeddb.ts`

## Split Detail Page (src/routes/split/[id]/+page.svelte)
- `src/lib/components/ui/Card.svelte`
- `src/lib/components/ui/Button.svelte`
- `src/lib/services/offline/indexeddb.ts`
- `src/lib/services/api/index.ts`
- `src/lib/types/split.ts`

## Global Layout (src/routes/(app)/+layout.svelte)
- `src/app.css`
- `src/lib/components/layout/AppShell.svelte`
- `src/lib/components/layout/OfflineBanner.svelte`
- `src/lib/components/layout/BottomNav.svelte`
- `src/lib/components/ui/ErrorBoundary.svelte`
