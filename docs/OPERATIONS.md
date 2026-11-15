# Operations Guide

Three containers, defined in `docker/docker-compose.yml`: `web` (static SvelteKit build, port 15173), `api` (FastAPI, port 18000), `postgres` (port 15432, volume `postgres_data`).

There is no metrics endpoint, error tracker or alerting. Logs are container stdout: `make logs`.

## Deployment

`.github/workflows/ci-master.yml`, on push to `master`, after the test job passes:

1. Builds `docker/Dockerfile.web` and `docker/Dockerfile.api` (linux/arm64) and pushes `split-bill-web:latest` / `split-bill-api:latest` to the registry.
2. On the VPS runner: copies `docker/docker-compose.yml` into `/home/ubuntu/composes/split-bill/docker/`, then pulls and recreates the containers using the `.env` in `/home/ubuntu/composes/split-bill/`.

The api container applies alembic migrations on every start (`alembic upgrade head`), then starts uvicorn.

Manual deploy on a server with the repo checked out and a `.env` at the root:

```bash
make up      # build + start
make ps      # status
make logs    # follow logs
make down    # stop
```

## Configuration

Runtime (`.env`, read by compose): `API_KEY`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL_NAME`, `APP_BASE_URL`, `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.

Build time (baked into the web bundle): `VITE_FASTAPI_API_URL`, `VITE_API_KEY`. In CI these come from the repository variable `VITE_FASTAPI_API_URL` and the secret `VITE_API_KEY`; locally compose passes `API_KEY` as `VITE_API_KEY`.

See `.env.example` for the list.

## Health

```bash
curl http://localhost:18000/health/
```

## Backup & Recovery

Postgres is the only state on the server (groups, templates, payments). Splits and history live in each user's browser (IndexedDB) and are not backed up.

```bash
# Backup
docker exec split-bill-postgres pg_dump -U postgres splitbill | gzip > splitbill-$(date +%Y%m%d).sql.gz

# Restore
gunzip -c splitbill-YYYYMMDD.sql.gz | docker exec -i split-bill-postgres psql -U postgres splitbill
```

## Security Checklist

#### Infrastructure

- [ ] Firewall enabled
- [ ] Only required ports open (80, 443) behind a reverse proxy with HTTPS
- [ ] SSH key-based auth only (no passwords)
- [ ] Postgres port (15432) not exposed publicly

#### Application

- [ ] Strong `API_KEY` (32+ random chars) and non-default `POSTGRES_PASSWORD`
- [ ] No secrets in logs

Note: `VITE_API_KEY` ships in the public web bundle, so the API key is not a secret from users. See the identity/auth item in [TODO.md](TODO.md).

## Related Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [Development Guide](DEVELOPMENT.md)
- [API Reference](API.md)
