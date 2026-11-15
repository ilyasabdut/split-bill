# Split Bill — Project Audit

**Date**: 2026-11-15 · **Branch**: `refactor` (221 commits, 25 files / ~1,300 lines uncommitted)
**Method**: read the tree, traced imports, ran the test suites and type check. Every claim below was checked against code, not against the existing docs.

---

## 1. The goal

A mobile-first PWA for young adults to split a bill with friends in under a minute:

1. Snap a receipt → AI OCR extracts items (OpenRouter).
2. Assign items / pick a split method (equal, %, by item), add tax and tip.
3. Get per-person totals and **share a link** so friends see what they owe.
4. Track who has paid; keep history, groups and reusable templates.

Stack: SvelteKit 5 static PWA (`web/`) + FastAPI (`api/`) + Postgres, Redis (Valkey), Garage S3, all in Docker Compose, deployed to a VPS via GitHub Actions.

The `refactor` branch's specific goal (per `docs/plans/2026-02-13-mobile-first-pwa-redesign.md`): replace the Streamlit frontend with the SvelteKit PWA, with offline mode and background sync.

---

## 2. What is actually implemented

| Area | State | Evidence |
|---|---|---|
| Receipt OCR | Works | `POST /receipts/upload` in `api/src/main.py:580` → `services/openrouter_ocr.py`; called from `web/src/routes/receipt/+page.svelte` |
| Split calculation (equal / % / by item, rounding, tax, tip) | Works, client-side | `web/src/routes/split/+page.svelte` + `lib/services/offline/calc.ts`; also calls `POST /splits/calculate` |
| Split detail, mark-as-paid, settlement graph, QR | Works, **local only** | `routes/split/[id]/+page.svelte` reads/writes IndexedDB |
| History with filters and search | Works, local only | `routes/history/+page.svelte` over IndexedDB |
| Dashboard stats / insights | Works, local only | derived from IndexedDB |
| Groups CRUD | Works against Postgres | `api/src/routers/groups.py`, `routes/groups/*` |
| Templates CRUD | Works against Postgres | `api/src/routers/templates.py` |
| Currency rates / convert | Works, with hardcoded fallback | `routers/currency.py`, `ui/CurrencyConverter.svelte` |
| Dark mode, design system, a11y passes | Done | six audit rounds in `docs/frontend-audit-report*.md` |
| PWA manifest + service worker precache | Configured | `web/vite.config.ts` (VitePWA) |
| Docker Compose (web, api, valkey, garage, postgres) | Present | `docker/docker-compose.yml` |
| Streamlit removal | Done in code | no `app/` directory left |

---

## 3. In progress / half-done

These have UI or code, but do not do what they claim.

| Item | What's really there |
|---|---|
| **Shareable links** (the headline feature) | `GET /splits/view/{id}` returns hardcoded "Alice and Bob" mock data (`main.py:553`). Splits are never written to Postgres or Garage; they live only in the creator's IndexedDB. A friend opening the link sees "Split not found". |
| **Users / auth** | Frontend hardcodes `owner_id: 1` / `user_id: 1` (`routes/groups/new/+page.svelte:86,101`). One shared API key baked into the bundle via `VITE_API_KEY`. Everyone is user 1. |
| **Server-side payments** | `routers/payments.py` exists and works, but the frontend never calls it (`lib/services/api/payments.ts` has zero importers, and calls two endpoints that do not exist). Payment state is IndexedDB only. |
| **Server analytics** | `routers/analytics.py` queries the `splits` table, which nothing ever inserts into. Always returns zeros. |
| **Offline queue / background sync** | `lib/services/offline/queue.ts` is only ever *read* (pending count). The only code that enqueues is `UploadZone.svelte`, which no page uses. No Background Sync registration anywhere. |
| **Offline fallback** | Workbox `navigateFallback: '/offline'` points to a route that does not exist. |
| **Send reminder** | `setTimeout(1500)` then a success message (`routes/send-reminder/+page.svelte:45`). |
| **Notifications / sound toggles** | Persist a boolean to localStorage; nothing reads it. |
| **Settings "API key"** | Copies a fake masked string (`settings/+page.svelte:75`). |
| **Activity feed on split detail** | Fabricated: three fake events with fixed +1h / +2h timestamps (`split/[id]/+page.svelte:82`). |
| **"Export CSV"** | Exports JSON. |
| **Backend modularisation** | Abandoned midway. `main.py` (911 lines) defines health/metrics/splits/receipts inline; `routers/{health,splits,receipts}.py` are orphaned duplicates. `routers/__init__.py` still says "moved to backup files". |
| **Uncommitted work** | 25 modified files including most pages, plus `docs/TODO.md` fully rewritten. Not committed since the v6 audit commits. |

### Verification status (ran today)

| Check | Result |
|---|---|
| `uv run pytest api/tests` | **Does not collect.** 6 collection errors: `db/database.py` `Settings` forbids extra env keys, and the root `.env` has `garage_*`, `redis_url`. Same failure will hit the API if started from the repo root, since `main.py` only catches `ImportError`. |
| `bunx vitest run` | **0 tests run, 13 files fail.** `vitest.config.js` points at `setup.js`; the file is `setup.ts`. |
| `bun run check` | **129 errors, 15 warnings** in 48 files. |
| `make test` | Ends in `|| true`, so it always "passes". |
| CI (`.github/workflows/ci-master.yml`) | Builds `docker/Dockerfile` (Streamlit, deleted) and deploys `docker-compose.prod.yml` (does not exist). Will fail on the next push to master. Never builds the web image. |
| E2E | `playwright.config.ts` targets `./e2e`, which does not exist. |

So `docs/TODO.md` marking every phase "DONE" and the README's "Production Ready" are not accurate.

---

## 4. Not touched

- Real identity: sign-up/login, per-user data, any authorisation on groups/templates/payments.
- Persisting splits server-side (the `splits` table and the Garage bucket are provisioned and unused).
- Receipt image storage (`storage_utils.py` is never called).
- Push notifications / actual reminders (WhatsApp, email, anything).
- Multi-device sync of history.
- Debt simplification across multiple splits within a group.
- E2E tests; any working CI test stage.
- Production deployment of the SvelteKit app.
- Docs refresh: README still describes `app/` Streamlit, `api_main.py`, `integrated_api.py`, Dexie, Skeleton UI and MinIO, none of which exist. ADR-004 is "Streamlit frontend".

---

## 5. Over-engineering audit (ponytail)

Ranked biggest cut first. Tags: `delete` dead code · `yagni` speculative · `native`/`stdlib` platform does it · `shrink` same logic, less code.

### Backend

1. `delete:` the whole "enterprise" core layer, imported by nothing in the running app: `core/{config,settings,logging,logging_config,metrics,monitoring,security,exceptions,sentry_config}.py`, `src/monitoring.py`, `src/cache_integration.py`, `utils/imports.py`, `db/base.py`. Replacement: nothing. `main.py` already has its own logger, rate limiter and API-key check. [api/src/core, api/src]
2. `delete:` orphaned router duplicates `routers/{health,splits,receipts}.py`, the two `.backup` files, and `dependencies.py` + `models/schemas.py` which only they import. `routers/monitoring.py` is imported but never `include_router`ed. [api/src/routers]
3. `delete:` ~4,800 lines of tests that only test items 1–2 (`test_core_*`, `test_settings`, `test_schemas`, `test_storage_utils`, `test_routers_{health,monitoring,receipts,splits}`, `test_summary`, `test_sample`, `conftest_unit.py`). They inflate the coverage number for code that never runs. [api/tests/unit]
4. `delete:` `services/split_logic.py` (343 lines). Production uses the 90-line `calculate_split` in `main.py:293`; only tests import the service. Pick one; keep the tested one and import it. [api/src/services]
5. `delete:` `services/storage_utils.py` (261 lines, MinIO client, zero callers) and with it the **Garage container**, its config and two volumes. Add back the day images are actually stored. [api/src/services, docker/]
6. `yagni:` **Redis/Valkey + `core/cache.py`** (347 lines) caches a pure arithmetic function that runs in microseconds. Replacement: nothing. Removes a container. [api/src/core/cache.py]
7. `shrink:` seven copy-pasted `try: __import__(...) except ImportError` blocks and `*_AVAILABLE` flags (~70 lines) → five plain `from routers.x import x_router` lines. A missing router should crash at startup, not silently vanish. [api/src/main.py:121-145, 780-840]
8. `delete:` `StructuredLogger`, `SimpleRateLimiter`, `MONITORING_DATA` and `/metrics` in `main.py`. A hobby app behind one API key has no scraper reading them. Uvicorn access logs cover it. [api/src/main.py:62-230, 414-447]
9. `delete:` 19 Python dependencies with no import in live code: `aioredis, chardet, charset-normalizer, cryptography, httptools, pandas, protobuf, pycryptodomex, python-jose, passlib, requests, sentry-sdk, slowapi, structlog, prometheus-client, loguru*, minio, psycopg2-binary, uvloop` (the last eight go once items 1 and 5 are deleted; `httptools`/`uvloop` are optional uvicorn speedups, keep if you care). Move `black, isort, mypy, pre-commit, pytest*` to the dev group. (*`loguru` is used once in `openrouter_ocr.py`; swap for stdlib `logging` like the rest.) [pyproject.toml]
10. `delete:` `api/count_backend_tests.py`, `api/count_coverage.py`, `api/test_db.py`, `scripts/demos/phase1_demo.py`, `api/src/ocr.jpeg` (323 KB in the source package), empty `src/middleware/`, empty `tests/fixtures/`.

### Frontend

11. `delete:` 12 components with zero usages (~1,100 lines): `ui/{Toggle,SummaryCard,Tabs,Select,SplitCard,StatCard,HeightTransition}`, `TemplateCard`, `GroupCard`, `features/split/{PersonManager,SplitResults}`, `features/receipt/UploadZone`. Pages inline the same markup instead. [web/src/lib/components]
12. `delete:` `lib/component-variants.ts` (85 lines). CLAUDE.md tells you to import from it; nothing does. [web/src/lib]
13. `delete:` `services/api/payments.ts`, `services/api/health.ts` (no importers), `services/offline/queue.ts` (nothing enqueues), and their tests. [web/src/lib/services]
14. `delete:` `playwright` from **runtime** `dependencies`, `@lightpanda/browser`, `@superdesign/cli`, `playwright.config.ts`, the `lightpanda:*` scripts and Make targets, `scripts/start-lightpanda.sh`. No e2e directory exists. Also `autoprefixer` (Tailwind 4 does it). [web/package.json]
15. `delete:` duplicate `vitest.config.js` (the broken one) and its tracked `vitest.config.js.timestamp-*.mjs`. `vite.config.ts` already has a correct `test` block. This alone un-breaks the web tests. [web/]
16. `delete:` `static/{generate-icons.js,create-png-icons.js,create-placeholders.sh}`. The PNGs are already generated and committed. [web/static]
17. `yagni:` 90% coverage thresholds in a suite that runs zero tests. [web/vite.config.ts]
18. `shrink:` three implementations of split math (`split/+page.svelte:121-150`, `offline/calc.ts`, and the API). The page computes locally *and* calls the API *and* falls back. Pick the client calc; it is the only one that works offline.

### Repo / docs

19. `delete:` six frontend audit reports + nine `design-progress/*.md` (4,810 lines of historical agent output). Git has them. [docs/]
20. `delete:` `docs/plans/…redesign.md` and `docs/refactor/…redesign.md` (same plan twice; `refactor/index.md` is a pasted terminal transcript), ADR-004 Streamlit, ADR-003 MinIO.
21. `delete:` `AGENTS.md` is a byte-identical copy of `CLAUDE.md` (both 11,420 bytes). Symlink it. `.omo/` is untracked agent state; gitignore it.
22. `shrink:` README 24 KB → one screen: what it is, `make up`, env vars.

**net: about -11,500 lines of code and tests, -5,000 lines of stale docs, -23 deps, -2 containers possible.**

Caveat: the `delete` findings for backend modules are based on import tracing across `api/src`. Tests import them, so deleting a module means deleting its test file in the same commit.

---

## 6. What I think

**The product is a good local-only bill calculator wearing a distributed-system costume.** The part users touch (scan → split → see totals) works and looks polished. Nearly everything described as infrastructure — caching, object storage, metrics, Sentry, JWT, structured logging, offline queue — is either unused or serving nothing.

Three honest observations:

1. **The core promise is the one thing missing.** "Split a bill and send friends a link" needs exactly one feature that does not exist: saving a split on the server and reading it back. The table, the model and the endpoint stub are all there. It is perhaps 40 lines. Six rounds of accessibility audits were done before this.
2. **The status docs are optimistic to the point of being wrong.** Every phase is ticked, yet no test suite runs, the type check has 129 errors and CI builds a deleted Dockerfile. The docs were written by whoever did the work, grading their own homework. Trust `make check`, not `TODO.md` — and first remove the `|| true`.
3. **Roughly half the repository is dead weight**, and it has a cost: it is why tests cannot collect (a dead settings module chain), why there are five containers for a two-container app, and why each new agent session burns context reading docs that describe a Streamlit app.

### Suggested order

1. **Commit or stash the 25 dirty files.** Everything else is risky on top of 1,300 uncommitted lines.
2. **Delete first** (section 5, items 1–5, 11–15, 19–21). Pure removal, no behaviour change, and it makes the next steps small.
3. **Make the checks tell the truth**: drop `vitest.config.js`, add `extra = "ignore"` to the DB `Settings`, remove `|| true`, fix CI to build `Dockerfile.web` + `Dockerfile.api`.
4. **Build the shareable link**: `POST /splits/calculate` inserts a `Split` row; `GET /splits/view/{id}` reads it without auth; `split/[id]` falls back to the API when IndexedDB misses.
5. **Then decide on identity.** Either go anonymous-by-link (drop `users`, groups by share code — fits the "no awkward money conversations" brief and is far less code) or add real auth. Do not keep `owner_id: 1`.
6. Only after that: reminders, server payments, sync.

I would resist adding anything new until step 4 ships. It is the difference between a demo and the product described in section 1.

---

## 7. Status after cleanup

Sections 3-5 describe the repository **before** the cleanup (checkpoint commit `3d5fe94`). The cleanup then removed the dead backend layer, Redis/Valkey, Garage/MinIO, the unused frontend code and tooling, and the stale docs listed in section 5, and fixed the Makefile, Docker and CI setup. The stack is now web + api + postgres.

For what is still open, see [TODO.md](TODO.md). For whether the checks pass, run `make check`.
