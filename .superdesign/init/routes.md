# Routes

Page and route structure for Split Bill (SvelteKit).

## Route Mapping
- `/` -> `src/routes/(app)/+page.svelte` (Home/Dashboard)
- `/receipt` -> `src/routes/receipt/+page.svelte` (Receipt Upload)
- `/split` -> `src/routes/split/+page.svelte` (Create Split)
- `/split/[id]` -> `src/routes/split/[id]/+page.svelte` (Split Detail)
- `/history` -> `src/routes/history/+page.svelte` (History)
- `/settings` -> `src/routes/settings/+page.svelte` (Settings)
- `+error.svelte` -> Global error page

## Layouts
- `src/routes/(app)/+layout.svelte` -> Main application layout with AppShell and BottomNav.
