# Integration Audit & TODO

**Last Updated**: 2026-05-17
**Status**: Comprehensive audit of all endpoints, frontend integrations, buttons, and filters.

---

## Legend

- [x] Working end-to-end
- [~] Partially working (UI exists, logic incomplete or uses mock/hardcoded data)
- [ ] Not connected (UI placeholder only, no backend integration)

---

## 1. API Endpoints

### Core (in `api/src/main.py` — monolith)

| Method | Endpoint | Rate Limit | Status | Notes |
|--------|----------|-----------|--------|-------|
| GET | `/` | — | [x] | Returns API info |
| GET | `/health/` | — | [x] | Health check with cache/monitoring stats |
| GET | `/metrics/` | — | [x] | Application metrics |
| POST | `/receipts/upload` | 30/min | [x] | OCR via OpenRouter, returns parsed items |
| POST | `/splits/calculate` | 30/min | [x] | Core split calculation with caching |
| GET | `/splits/view/{split_id}` | 100/min | [~] | Returns mock data if not in cache |

### Modular Routers (in `api/src/routers/` — require PostgreSQL)

| Method | Endpoint | Status | Notes |
|--------|----------|--------|-------|
| **Groups** | | | |
| POST | `/groups/` | [x] | Creates group with owner_id |
| GET | `/groups/` | [x] | List groups (filter by owner_id) |
| GET | `/groups/{id}` | [x] | Get single group |
| PUT | `/groups/{id}` | [x] | Update group name |
| DELETE | `/groups/{id}` | [x] | Delete group |
| POST | `/groups/{id}/members` | [x] | Add member |
| GET | `/groups/{id}/members` | [x] | List members |
| DELETE | `/groups/{id}/members/{user_id}` | [x] | Remove member |
| **Templates** | | | |
| POST | `/templates/` | [x] | Creates template with user_id + config |
| GET | `/templates/` | [x] | List (filter by user_id) |
| GET | `/templates/{id}` | [x] | Get single |
| PUT | `/templates/{id}` | [x] | Update |
| DELETE | `/templates/{id}` | [x] | Delete |
| **Payments** | | | |
| POST | `/payments/` | [x] | Create payment record |
| GET | `/payments/` | [x] | List (filter by split_id, status) |
| GET | `/payments/{id}` | [x] | Get single |
| PUT | `/payments/{id}` | [x] | Update status (unpaid→paid→confirmed) |
| DELETE | `/payments/{id}` | [x] | Delete |
| GET | `/payments/split/{split_id}/summary` | [x] | Payment summary for a split |
| **Analytics** | | | |
| GET | `/analytics/users/{user_id}/stats` | [x] | User statistics |
| GET | `/analytics/overall` | [x] | App-wide statistics |
| GET | `/analytics/currencies` | [x] | Currency usage (last N days) |
| GET | `/analytics/trends` | [x] | Split creation trends |
| **Currency** | | | |
| GET | `/currency/rates` | [x] | Exchange rate lookup |
| POST | `/currency/convert` | [x] | Currency conversion |

**Key Finding**: Groups, Templates, Payments, Analytics, and Currency routers all depend on `src.db.deps.get_db` (PostgreSQL via SQLAlchemy async). These routers will fail at runtime without a running PostgreSQL instance and completed migrations.

---

## 2. Frontend Pages

### Dashboard (`/` — `web/src/routes/(app)/+page.svelte`)

| Element | Type | Status | Notes |
|---------|------|--------|-------|
| Currency pill (IDR selector) | Button | [x] | Opens CurrencyConverter modal, API with fallback |
| "New Split" button | Link | [x] | Navigates to `/split` |
| "Scan Receipt" button | Link | [x] | Navigates to `/receipt` |
| Saved Templates (Lunch, Rent, Trip) | Buttons | [x] | Loaded from API, navigate to /split |
| "Edit" templates button | Button | [x] | Navigates to /split page |
| "Add" template button | Button | [x] | Navigates to /split page (use Save as Template) |
| Quick Stats (This month, Settled, Pending) | Display | [x] | Derived from IndexedDB |
| Spending Insights chart | Display | [x] | Dynamic chart from IndexedDB data |
| Split count badge | Link | [x] | Shows real count, links to `/history` |
| Your Groups (Roomies, Game Crew, Hikers) | Cards | [x] | Loaded from API, dynamic rendering |
| "+ Create Group" link | Link | [x] | Navigates to `/groups/new` |
| Activity Feed | Display | [x] | Populated from IndexedDB splits |
| Recent Splits | Cards | [x] | Real data from IndexedDB with dynamic initials |
| "View all" recent splits | Link | [x] | Navigates to `/history` |
| "Details" button on split cards | Link | [x] | Navigates to `/split/{id}` |
| Notifications bell | Button | [x] | Navigates to `/send-reminder` |
| Profile button | Button | [x] | Navigates to `/settings` |
| Scanning Tips card | Display | [x] | Static content |

### Receipt Page (`/receipt`)

| Element | Type | Status | Notes |
|---------|------|--------|-------|
| File upload (scan receipt) | Input | [x] | Calls `/receipts/upload` API with error handling |
| Camera button | Button | [x] | Requests camera permission, calls OCR API |
| Item list (add/edit/remove) | Form | [x] | Full CRUD with validation, works locally |
| Tax toggle | Switch | [x] | Toggles `taxEnabled` state, reflects in UI |
| "Edit Rate" button | Button | [x] | Inline edit for tax percentage |
| "Share" button | Button | [x] | Uses Web Share API / clipboard fallback |
| "Confirm" button | Button | [x] | Validates items, stores in `receiptStore`, navigates to `/split` |
| Back arrow | Link | [x] | Navigates to `/` |

### Split Page (`/split`)

| Element | Type | Status | Notes |
|---------|------|--------|-------|
| Bill amount input | Input | [x] | `bind:value={billAmount}` — updates state |
| Tax input | Input | [x] | Bound to `tax` state |
| Tip input | Input | [x] | Bound to `tip` state |
| Quick tip buttons (15%, 18%, 20%) | Buttons | [x] | Updates tip based on percentage |
| "Custom" tip button | Button | [x] | Shows custom tip amount input |
| Currency selector | Button | [x] | CurrencySelector component with real options |
| "Auto-detect" tax button | Button | [x] | Sets tax to 11% PPN |
| Smart Rounding (Down/Exact/Up) | Toggle | [x] | Applied in calculation via `applyRounding()` |
| Split Method (Equal/% Split/By Item) | Toggle | [x] | All three methods work with full calculation logic |
| People manager (add/remove/rename) | Form | [x] | Full CRUD with validation |
| "Assign Items" button per person | Button | [x] | Switches to "By Item" split method |
| "Calculate Split" button | Button | [x] | Calls `splitsService.calculate()` API, navigates to `/split/{id}` |
| "Save as Template" button | Button | [x] | Saves to API with IndexedDB fallback |
| Back arrow | Link | [x] | Navigates to `/` |

### Split Detail (`/split/[id]`)

| Element | Type | Status | Notes |
|---------|------|--------|-------|
| Split results display | Display | [x] | Loads from IndexedDB, shows real data |
| Settlement graph | Display | [x] | Computed from split results |
| Share functionality | Button | [x] | Web Share API / clipboard fallback |
| Payment status | Display | [x] | Persists to IndexedDB, survives reload |
| Mark as Paid | Button | [x] | Updates IndexedDB, updates UI |
| Dynamic title | Display | [x] | Shows merchant or people names |
| Total receivable | Display | [x] | Computed from split results |

### History Page (`/history`)

| Element | Type | Status | Notes |
|---------|------|--------|-------|
| Split list from IndexedDB | Display | [x] | Loads from local IndexedDB, sorts by date |
| Filter tabs (All/Unpaid/Completed/Groups) | Tabs | [x] | Functional filtering with derived state |
| Search button | Button | [x] | Toggles search input, filters by name/title |
| Currency selector | Button | [x] | CurrencySelector component |
| Monthly Spending Summary | Display | [x] | Derived from IndexedDB (current month) |
| Split count badge | Display | [x] | Shows total split count |
| Summary Chips (People, Pending) | Display | [x] | Derived from IndexedDB data |
| Settlement Summary (Owed to You) | Cards | [x] | Computed from unpaid splits |
| Split card links | Links | [x] | Navigate to `/split/{id}` |
| Loading skeleton | Display | [x] | Shows while IndexedDB loads |

### Settings Page (`/settings`)

| Element | Type | Status | Notes |
|---------|------|--------|-------|
| Dark mode toggle | Switch | [x] | Persists to localStorage, toggles `dark` class |
| Notifications toggle | Switch | [~] | Persists to localStorage, no notification system |
| Sound effects toggle | Switch | [~] | Persists to localStorage, no sound system |
| Currency initialization | Logic | [x] | Calls `currencyStore.init()` |
| Copy API Key | Button | [x] | Copies to clipboard with feedback |
| Clear data | Button | [x] | Deletes correct IndexedDB (`split-bill-db`) |

### Groups Pages

| Page | Status | Notes |
|------|--------|-------|
| `/groups/new` | [x] | Form creates group via API |
| `/groups/[id]` | [x] | Detail view loads from API |

### Send Reminder (`/send-reminder`)

| Page | Status | Notes |
|------|--------|-------|
| `/send-reminder` | [x] | Member selection, custom message, simulated send (no notification backend) |

---

## 3. Stores & Services Integration Map

| Store | Initialized By | API Service Used | Status |
|-------|---------------|-----------------|--------|
| `currencyStore` | Dashboard, Receipt, Split, History, Settings | `currency` service | [x] Init works, API returns live rates |
| `analyticsStore` | Dashboard, History | `analytics` service | [x] Calls `/analytics/overall`, graceful failure |
| `receiptStore` | Receipt → Split | None (local state) | [x] Passes data between pages |
| `splitStore` | Split page | `splitsService` | [x] Calculate endpoint works |
| `groupsStore` | Dashboard, Split page | `groups` service | [x] `loadGroups()` fetches from API |
| `templatesStore` | Dashboard, Split page | `templates` service | [x] `loadTemplates()` fetches from API |
| `offlineStore` | Split page | None (IndexedDB) | [x] Local offline queue |

---

## 4. Critical Integration Gaps

### High Priority (Core Flow Broken)

1. ~~**Receipt OCR not connected**~~ — **FIXED**: Receipt page calls `/receipts/upload` API with proper error handling.

2. ~~**Bill amount input not bound**~~ — **FIXED**: Already has `bind:value={billAmount}`.

3. ~~**Filter tabs on History are dead**~~ — **FIXED**: Functional filter buttons with derived state.

### Medium Priority (Features Incomplete)

4. ~~**"By Item" split method**~~ — **FIXED**: Item assignment UI with per-person toggle buttons, proportional tax/tip distribution.

5. ~~**Smart Rounding not applied**~~ — **FIXED**: Applied in calculation via `applyRounding()`.

6. **Templates functional** — "Save as Template" saves to API. Dashboard loads templates from API.

7. **Groups functional** — Dashboard loads groups from API. Create group page calls API. Detail page loads from API.

8. ~~**Payment tracking missing**~~ — **FIXED**: IndexedDB-based payment tracking with persistence.

9. ~~**Currency conversion not connected**~~ — **FIXED**: CurrencyConverter calls API with 3s timeout and hardcoded fallback.

### Low Priority (Polish/Enhancement)

10. ~~**Dead links**~~ — **FIXED**: All `href="#..."` links removed or replaced with real navigation.

11. ~~**Notifications/Profile buttons**~~ — **FIXED**: Navigate to `/send-reminder` and `/settings`.

12. ~~**Analytics data hardcoded**~~ — **FIXED**: Dashboard and history derive stats from IndexedDB.

13. ~~**Send Reminder page**~~ — **FIXED**: Functional with member selection and simulated send.

---

## 5. Database Dependency

Features requiring PostgreSQL with migrations:

- Groups CRUD
- Templates CRUD
- Payments CRUD
- Analytics queries
- User management

**Current state**: The monolith `main.py` gracefully handles missing routers via try/except imports. The modular routers in `api/src/routers/` import from `src.db.deps` and `src.db.models` which require a running PostgreSQL instance.

---

## 6. Recommended Next Steps

### ~~Phase 1: Fix Core Flow (Receipt → Split → Result)~~ DONE
1. ~~Connect receipt page to `/receipts/upload` API~~
2. ~~Fix bill amount input binding on split page~~
3. ~~Verify split detail page displays results correctly~~
4. ~~Store split results in IndexedDB for history~~

### ~~Phase 2: Make Existing UI Functional~~ DONE
5. ~~Implement history filter tabs (filter by status from IndexedDB)~~
6. ~~Implement "% Split" and "By Item" split methods~~
7. ~~Apply smart rounding to calculations~~
8. ~~Connect currency converter to API~~

### Phase 3: Backend Features (Requires PostgreSQL) — DONE
9. ~~Verify PostgreSQL + migrations work with docker-compose~~ — PostgreSQL running locally, all tables exist
10. ~~Connect groups UI to groups API~~ — Dashboard, create, detail pages all use API
11. ~~Connect templates UI to templates API~~ — Dashboard loads from API, Save as Template uses API
12. ~~Connect payments API for server-side tracking~~ — Payments endpoints working

### ~~Phase 4: Polish~~ DONE
13. ~~Replace all `href="#..."` dead links with real navigation or remove~~
14. ~~Replace hardcoded dashboard data with real analytics~~
15. ~~Implement notifications system (send-reminder page)~~
16. ~~Add search, currency selectors, custom tip, tax edit~~

---

## Completed Phases (Historical)

- Phase 1: Modular Architecture & Code Quality
- Phase 2: Security Hardening (API Key auth, rate limiting, security headers)
- Phase 3: Performance & Caching (Redis integration)
- Phase 4: Production Integration (FastAPI routers, Docker)
- Phase 5: Frontend Integration (Streamlit → SvelteKit migration)
- Phase 6: Testing & QA (pytest framework, code quality tools)
- Phase 7: Monitoring & Observability (health, metrics, structured logging)
- Phase 8: UX Enhancements (mobile-responsive, accessibility, dark theme)
- Phase 9: SuperDesign UI Implementation (all 6 pages)

---

## Related Documents

- [Architecture Overview](ARCHITECTURE.md)
- [API Documentation](API.md)
- [Development Guide](DEVELOPMENT.md)
- [Operations Guide](OPERATIONS.md)
- [Architecture Decisions](ADR/)
