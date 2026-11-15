.PHONY: all help up down logs clean install start build rebuild-web check lint format test test-web web-check infra-up ps

COMPOSE = docker compose --env-file .env -f docker/docker-compose.yml

# Default target: show help
all: help

help:
	@echo "🧾 Split Bill - Development Commands"
	@echo "====================================="
	@echo ""
	@echo "Docker:"
	@echo "  make up              - Build & start web, api, postgres"
	@echo "  make down            - Stop all services"
	@echo "  make logs            - View logs (Ctrl+C to exit)"
	@echo "  make ps              - Show running containers"
	@echo "  make infra-up        - Start postgres only"
	@echo "  make rebuild-web     - Rebuild & restart web container"
	@echo "  make clean           - Remove build artifacts and volumes"
	@echo ""
	@echo "Development:"
	@echo "  make install         - Install dependencies"
	@echo "  make start           - Start dev servers locally"
	@echo "  make build           - Build web for production"
	@echo ""
	@echo "Quality:"
	@echo "  make check           - Lint + API tests + web check + web tests"
	@echo "  make lint            - Ruff"
	@echo "  make format          - Ruff --fix + prettier"
	@echo "  make test            - API tests"
	@echo "  make test-web        - Web tests"
	@echo "  make web-check       - svelte-check"

# ====================================
# Docker
# ====================================

# Build and start all services
up:
	$(COMPOSE) up --build -d
	@echo ""
	@echo "✅ Services started!"
	@echo "   Web: http://localhost:15173"
	@echo "   API: http://localhost:18000"

# Stop all services
down:
	$(COMPOSE) down

# View logs
logs:
	$(COMPOSE) logs -f

# Show running containers
ps:
	$(COMPOSE) ps

# Start postgres only (for local dev servers)
infra-up:
	$(COMPOSE) up -d postgres

# Rebuild web container and restart
rebuild-web:
	$(COMPOSE) up -d --build web

# Clean everything (including the postgres volume)
clean:
	rm -rf web/node_modules web/build web/.svelte-kit
	$(COMPOSE) down -v

# ====================================
# Development
# ====================================

# Install all dependencies
install:
	uv sync
	cd web && bun install

# Start local dev servers (not Docker)
start:
	@# Start API in background
	cd api && uv run python -m dotenv -f ../.env run uvicorn src.main:app --host 0.0.0.0 --port 18000 --reload &
	cd web && bun run dev

# Build for production
build:
	cd web && bun run build

# ====================================
# Quality Checks
# ====================================

# Run all quality checks
check: lint test web-check test-web
	@echo "✅ All checks passed!"

# Lint code
lint:
	uv run ruff check api

# Format code
format:
	uv run ruff check --fix api
	cd web && bun x prettier --write .

# Run API tests
test:
	uv run pytest api/tests -q

# Check web
web-check:
	cd web && bun run check

# Run web tests
test-web:
	cd web && bun run test
