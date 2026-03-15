.PHONY: all build up down logs clean rebuild-web install start help

# Default target: show help
all: help

help:
	@echo "🧾 Split Bill - Development Commands"
	@echo "====================================="
	@echo ""
	@echo "Quick Start:"
	@echo "  make up              - Build & start all services"
	@echo "  make down            - Stop all services"
	@echo "  make logs            - View logs (Ctrl+C to exit)"
	@echo ""
	@echo "Development:"
	@echo "  make install         - Install dependencies"
	@echo "  make start          - Start dev server locally"
	@echo "  make build          - Build for production"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean all build artifacts"
	@echo "  make rebuild-web    - Rebuild & restart web container"
	@echo "  make check          - Run quality checks"
	@echo ""
	@echo "Run 'make help' for all available commands"

# ====================================
# Quick Commands
# ====================================

# Build and start all services
up:
	@echo "🏗️  Building and starting all services..."
	cd web && bun run build
	docker-compose -f docker/docker-compose.yml up --build -d
	@echo ""
	@echo "✅ Services started!"
	@echo "   Web: http://localhost:15173"
	@echo "   API:  http://localhost:18000"
	@echo ""
	@echo "Run 'make logs' to follow logs"

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker-compose -f docker/docker-compose.yml down
	@echo "✅ Services stopped"

# View logs
logs:
	@echo "📋 Following logs (Ctrl+C to exit)..."
	docker-compose -f docker/docker-compose.yml logs -f

# Clean everything
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf web/node_modules web/build web/.svelte-kit
	docker-compose -f docker-compose.yml down -v
	@echo "✅ Clean complete"

# ====================================
# Development
# ====================================

# Install all dependencies
install:
	@echo "📦 Installing dependencies..."
	cd web && bun install

# Start local dev servers (not Docker)
start:
	@echo "🚀 Starting dev servers..."
	@# Start API in background
	cd api && uv run python -m dotenv -f ../.env run uvicorn src.main:app --host 0.0.0.0 --port 18000 --reload &
	cd web && bun run dev

# Build for production
build:
	@echo "🏗️  Building web application..."
	cd web && bun run build
	@echo "✅ Build complete!"

# Rebuild web container and restart
rebuild-web:
	@echo "🔄 Rebuilding web container..."
	cd web && bun run build
	docker-compose -f docker/docker-compose.yml up -d --build web
	@echo "✅ Web container rebuilt and restarted"

# ====================================
# Quality Checks
# ====================================

# Run all quality checks
check: lint web-check
	@echo "✅ All checks passed!"

# Lint code
lint:
	@echo "🔍 Running linter..."
	uv run ruff check .

# Format code
format:
	@echo "✨ Formatting code..."
	uv run ruff check --fix .
	cd web && bun x prettier --write . || true

# Run tests
test:
	@echo "🧪 Running tests..."
	cd api && python -m pytest tests/ -v || true

# Check web
web-check:
	@echo "🔍 Checking web..."
	cd web && bun run check

# Run web tests
test-web:
	@echo "🧪 Running web tests..."
	cd web && bun test

# Run E2E tests
test-e2e:
	@echo "🧪 Running E2E tests..."
	cd web && bun run test:e2e

# Start Lightpanda browser
lightpanda:start:
	@echo "🌐 Starting Lightpanda browser..."
	cd web && bun run lightpanda:start

# Fetch Lightpanda binaries
lightpanda:fetch:
	@echo "📥 Fetching Lightpanda binaries..."
	cd web && bun run lightpanda:fetch

# ====================================
# Infrastructure
# ====================================

# Start infrastructure only
infra-up:
	@echo "🔧 Starting infrastructure..."
	docker-compose -f docker/docker-compose.yml up -d redis garage postgres
	@echo "✅ Infrastructure started"

# Stop infrastructure
infra-down:
	@echo "🛑 Stopping infrastructure..."
	docker-compose -f docker/docker-compose.yml down
	@echo "✅ Infrastructure stopped"

# Show running containers
ps:
	docker-compose -f docker/docker-compose.yml ps
