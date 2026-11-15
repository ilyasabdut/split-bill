# Split Bill

Mobile-first PWA for splitting a bill with friends: snap a receipt, AI OCR extracts the items, assign them or pick a split method, add tax and tip, see who owes what.

Honest status and open work: [docs/PROJECT_AUDIT.md](docs/PROJECT_AUDIT.md), [docs/TODO.md](docs/TODO.md).

## Stack

- `web/` — SvelteKit 5 static PWA, Tailwind 4, Bun
- `api/` — FastAPI, SQLAlchemy + Alembic, uv; OCR via OpenRouter
- Postgres 16
- Docker Compose (`docker/`), deployed by GitHub Actions

## Quick start

```bash
cp .env.example .env    # fill in API_KEY and OPENROUTER_API_KEY
make up                 # web :15173, api :18000, postgres :15432
make logs
make down
```

Local dev servers instead of containers: `make install`, `make infra-up` (postgres only), `make start`. The api container runs migrations on start; locally run `cd api && uv run alembic upgrade head`.

`make help` lists every target.

## Environment variables

| Name | Used by |
|------|---------|
| `API_KEY` | api (bearer token) |
| `OPENROUTER_API_KEY`, `OPENROUTER_MODEL_NAME` | api (receipt OCR) |
| `APP_BASE_URL` | api (share links) |
| `DATABASE_URL` | api |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | postgres container (optional) |
| `VITE_API_KEY` | web dev server only (production: nginx in the web container adds `API_KEY`) |

## Tests

```bash
make check      # ruff + api tests + svelte-check + web tests
make test       # uv run pytest api/tests -q
make test-web   # cd web && bun run test
```

## Docs

[docs/](docs/README.md) — architecture, API, development, operations, ADRs. Design guidelines for agents: [CLAUDE.md](CLAUDE.md).
