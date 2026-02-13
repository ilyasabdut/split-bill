# Findings & Decisions

## Requirements
<!-- Captured from user request and Superdesign project -->
- Implement 6 enhanced Superdesign pages from project dfb58af2-075d-4e67-88b2-0138409ce0e9
- Multi-currency support: USD, NZD, YEN, IDR (default to IDR)
- Smart Split Intelligence: itemized receipts, auto-assign, quick templates
- Payment & Settlement: payment requests, settlement overview, bulk mark paid, reminders
- Social & Sharing: split groups, QR code sharing, activity feed, notes
- Smart Calculations: percentage tips (15%, 18%, 20%), tax auto-detection, currency conversion, rounding
- Data & Insights: spending analytics, recurring splits, balance summary, export formats
- UX Refinements: duplicate split, edit after creation, undo, dark mode, offline mode
- Quick Actions: multiple receipts, manual entry, clipboard paste
- Backend database implementation (currently NO DATABASE exists)
- Maintain offline-first PWA architecture

## Research Findings

### Frontend Architecture (SvelteKit)
- **Framework:** SvelteKit with Svelte 5 runes (`$state`, `$derived`, `$props`)
- **Routing:** File-based with route groups `(app)` and dynamic routes `[id]`
- **State Management:** Writable stores (receipt, split, offline)
- **Styling:** Tailwind CSS v4 with `@theme` syntax, primary color `#0ea5e9` (sky blue)
- **UI Components:** Button, Card, Input, Progress, ErrorBoundary (all in `components/ui/`)
- **Offline Storage:** IndexedDB with 3 stores (receipts, splits, offline_queue)
- **PWA:** Service worker with Workbox, network-first strategy
- **Design Pattern:** Mobile-first, 44px min touch targets, safe area insets

### Backend Current State (FastAPI)
- **Framework:** FastAPI with Redis caching ONLY
- **Critical Finding:** NO DATABASE - everything is ephemeral (Redis cache with 1-hour TTL)
- **Endpoints:** `/receipts/upload`, `/splits/calculate`, `/splits/view/{id}`, `/health`, `/metrics`
- **Auth:** API Key (Bearer token), not user-specific
- **OCR:** OpenRouter API (Mistral model) for receipt processing
- **Storage:** MinIO for receipt images
- **Missing:** Persistent storage, user accounts, groups, templates, payment tracking, analytics

### Backend Gaps Analysis
**Must Implement:**
1. **Database layer** (PostgreSQL) - BLOCKING for all other features
2. **User authentication** - Required for groups/templates ownership
3. **Groups CRUD** (`/groups/*` endpoints)
4. **Templates CRUD** (`/templates/*` endpoints)
5. **Payment tracking** (`/splits/{id}/payments/*` endpoints)
6. **Analytics** (`/analytics/*` endpoints)
7. **Currency support** (add currency field to all models, conversion service)
8. **Permanent history** (`/splits/history` with pagination)

### Superdesign Enhanced Features by Page
**Home Dashboard:**
- Currency selector pill (IDR default)
- Saved templates section (Lunch, Rent, Trip + Add)
- Your Groups section (Roommates, Game Crew, Hikers)
- Activity feed (recent actions by people)
- Spending insights card with monthly trends chart
- Recent splits with payment status badges

**Receipt Scan:**
- Live item detection list during OCR
- Tax recognition toggle with manual override
- Auto-detected currency display
- OCR confidence score badge (%)
- Share receipt option

**Create Split:**
- Currency selector at top
- Quick tip buttons (15%, 18%, 20%, custom)
- Tax auto-detect with manual override
- Line item assignment to specific people
- Smart rounding preferences

**Split Detail:**
- Settlement graph showing who owes whom
- Itemized breakdown expandable per person
- Activity timeline (who joined, who paid)
- Payment request buttons (Venmo, PayPal links)
- QR code sharing
- Mark as Paid action
- Add notes to split

**History:**
- Filter tabs (All, Unpaid, Paid, Groups)
- Settlement summary section (who owes you, who you owe)
- Monthly spending summary card
- Split cards with payment status badges
- Analytics tab with charts

**Settings:**
- Currency selector (USD, NZD, YEN, IDR)
- Dark mode toggle
- Sound preferences
- Groups management section
- Analytics toggle
- App version info

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| PostgreSQL for database | Production-ready, reliable, good Python support with SQLAlchemy |
| SQLAlchemy + Alembic | Industry standard ORM, type-safe, migration management |
| Add user authentication | Groups and templates need user ownership, session management |
| Hybrid database + cache | Permanent storage in DB, frequently accessed data in Redis cache |
| Currency conversion API | Use free tier exchange rate API (e.g., exchangerate-api.io) with daily caching |
| Payment links (not integration) | Generate Venmo/PayPal links instead of direct API (avoids complex OAuth) |
| Extend IndexedDB schema | Add groups, templates, currency stores for offline support |
| Pre-computed analytics | Calculate aggregations on write, cache results for fast reads |
| Keep offline-first architecture | All new features must work offline with queue sync |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| Backend has no database | Must implement full database layer before any new features |
| Splits expire after 1 hour (Redis TTL) | Migrate to permanent database storage with Redis as cache |
| No user accounts exist | Must add authentication system for groups/templates |
| Currency not in data models | Add currency field to ReceiptData, SplitResults, all financial models |

## Resources
- Superdesign project: https://p.superdesign.dev/draft/4f028cbb-335a-41d0-9228-0e0c0407160f
- Current frontend: `/Users/ilyasabdut/Projects/hobby/split-bill/web/src/`
- Current backend: `/Users/ilyasabdut/Projects/hobby/split-bill/api/src/`
- IndexedDB service: `web/src/lib/services/offline/indexeddb.ts`
- API client: `web/src/lib/services/api/client.ts`
- Backend schemas: `api/src/models/schemas.py`
- Backend routers: `api/src/routers/`

## Visual/Browser Findings
<!-- From Superdesign Enhanced Dashboard HTML -->
- Clean, cartoony aesthetic with rounded corners (xl/2xl/3xl radius)
- Sky blue theme (#0ea5e9) with gradient backgrounds
- Currency pill component with flag emoji (Rp for IDR)
- Template cards: 52px icons, orange/emerald/sky/slate colors
- Group cards: 160px width, icon + member count + "Last split Xd ago"
- Activity feed: 8px avatar circles with initials
- Spending insights: Dark slate card with simple bar chart
- Recent splits: Expandable cards with avatar stacks and "Details" button
- Bottom nav: 4 items (Home active, History, Scan +, Settings)
- All touch targets 44px+ minimum
- Safe area padding for mobile notches
