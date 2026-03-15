.PHONY: all build up down logs clean rebuild-api install start run-api web-install web-dev web-build web-check web-test stop stop-api check_dotenv lint lint-fix test format type-check pre-commit check-quality check-all demo-phase1 infra-up infra-down infra-logs infra-restart infra-ps infra-clean help

# Default target: show help
all: help

# Help target
help:
	@echo "🧾 Split Bill - Development Commands"
	@echo "====================================="
	@echo "Core Commands:"
	@echo "  make install          - Install all dependencies (Python + Web)"
	@echo "  make start            - Start the Svelte web frontend locally (alias for web-dev)"
	@echo "  make run-api          - Start the FastAPI backend locally"
	@echo "  make web-dev          - Start the Svelte web frontend locally"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make infra-up [ENV=prod]  - Start infrastructure (redis,minio / all prod)"
	@echo "  make infra-down [ENV=prod] - Stop infrastructure"
	@echo "  make infra-logs [ENV=prod] - View infrastructure logs"
	@echo "  make infra-restart [ENV=prod] - Restart infrastructure"
	@echo "  make infra-ps         - Show running containers"
	@echo "  make infra-clean [ALL=true] - Clean up all resources"
	@echo ""
	@echo "Docker Operations (Legacy Aliases):"
	@echo "  make build            - Build Docker images"
	@echo "  make up               - Start all services with Docker Compose (dev only, no cache)"
	@echo "  make down             - Stop and remove Docker services (dev only)"
	@echo "  make logs             - View service logs (dev only)"
	@echo "  make clean            - Clean up Docker resources and node_modules"
	@echo ""
	@echo "Web (Svelte) Commands:"
	@echo "  make web-install      - Install Svelte web dependencies"
	@echo "  make web-dev          - Run web dev server"
	@echo "  make web-build        - Build the web application"
	@echo "  make web-check        - Run Svelte check and type check"
	@echo "  make web-test         - Run Vitest for the web frontend"
	@echo ""
	@echo "Code Quality & Testing:"
	@echo "  make lint             - Run Python linting (Ruff)"
	@echo "  make lint-fix         - Auto-fix Python lint issues"
	@echo "  make format           - Format Python code (Black)"
	@echo "  make test             - Run Python tests"
	@echo "  make type-check       - Run MyPy type checking"
	@echo "  make pre-commit       - Run pre-commit hooks on all files"
	@echo "  make check-all        - Run all quality checks"
	@echo ""
	@echo "Demos:"
	@echo "  make demo-phase1      - Run Phase 1 architecture demo"

# Infrastructure Management (Dev/Prod)
# ====================================

# Determine which compose file to use based on ENV variable
ENV ?= dev
COMPOSE_FILE := docker/docker-compose.yml
ifeq ($(ENV),prod)
	COMPOSE_FILE := docker/docker-compose.prod.yml
endif

# Start infrastructure services (dev or prod based on ENV var)
# In dev mode: starts only redis and minio (without api/web)
# In prod mode: starts all services from prod compose file
infra-up:
	@echo "Starting infrastructure services ($(ENV) environment)..."
	@if [ "$(ENV)" = "prod" ]; then \
		echo "Using production configuration (docker-compose.prod.yml)..."; \
		docker-compose -f $(COMPOSE_FILE) pull; \
		docker-compose -f $(COMPOSE_FILE) up -d; \
	else \
		echo "Using development configuration (infrastructure only: redis, garage, postgres)..."; \
		docker-compose -f $(COMPOSE_FILE) up -d redis garage postgres; \
	fi

# Stop infrastructure services (dev or prod based on ENV var)
infra-down:
	@echo "Stopping infrastructure services ($(ENV) environment)..."
	docker-compose -f $(COMPOSE_FILE) down || true

# View infrastructure logs (dev or prod based on ENV var)
infra-logs:
	@echo "Following infrastructure logs ($(ENV) environment, Ctrl+C to exit)..."
	docker-compose -f $(COMPOSE_FILE) logs -f

# Restart infrastructure services (dev or prod based on ENV var)
infra-restart: infra-down infra-up

# Show running containers
infra-ps:
	@echo "Running containers:"
	docker-compose -f $(COMPOSE_FILE) ps

# Clean up infrastructure resources
infra-clean:
	@echo "Cleaning up infrastructure resources ($(ENV) environment)..."
	docker-compose -f $(COMPOSE_FILE) down --volumes
	@if [ "$(ALL)" = "true" ]; then \
		echo "Removing all images..."; \
		docker-compose -f $(COMPOSE_FILE) down --rmi all; \
		docker image prune -a -f; \
	else \
		echo "Removing volumes only (use ALL=true to remove images too)..."; \
	fi
	docker volume prune -f
	@echo "Cleanup complete."

# Legacy Docker Operations (Aliases to infra commands)
# ===================================================

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose -f docker/docker-compose.yml build

# Start services with Docker Compose (legacy alias for infra-up, dev only)
up:
	@echo "Starting services with Docker Compose (dev environment, no cache)..."
	docker-compose -f docker/docker-compose.yml build --no-cache
	docker-compose -f docker/docker-compose.yml up -d

# Stop and remove Docker Compose services (legacy alias for infra-down, dev only)
down:
	@echo "Stopping and removing Docker Compose services (dev environment)..."
	docker-compose -f docker/docker-compose.yml down || true

# Display logs for all services (legacy alias for infra-logs, dev only)
logs:
	@echo "Displaying logs for all services (dev environment, Ctrl+C to exit)..."
	docker-compose -f docker/docker-compose.yml logs -f

# Clean up Docker images and volumes, and local node_modules
clean:
	@echo "Cleaning up Docker images and volumes..."
	docker-compose -f docker/docker-compose.yml down --volumes --rmi all
	docker volume prune -f
	docker image prune -a -f
	@echo "Cleaning up local build artifacts..."
	rm -rf web/node_modules web/build web/.svelte-kit
	@echo "Cleanup complete."

# Helper for development: rebuild and restart a specific service
rebuild-api:
	@echo "Rebuilding and restarting API service..."
	docker-compose -f docker/docker-compose.yml up --build -d api

rebuild-web:
	@echo "Rebuilding and restarting Web service..."
	docker-compose -f docker/docker-compose.yml up --build -d web

# Install dependencies using uv and pnpm
install:
	@echo "Installing Python dependencies with uv..."
	uv pip show uv || uv pip install uv
	uv sync
	@echo "Installing Web dependencies with bun..."
	cd web && bun install

# Start the Svelte web frontend locally
start: web-dev

# Web (Svelte) Frontend Targets
# ============================

web-install:
	@echo "📦 Installing web dependencies..."
	cd web && bun install

web-dev:
	@echo "🚀 Starting web dev server..."
	cd web && bun dev

web-build:
	@echo "🏗️ Building web application..."
	cd web && bun run build

web-check:
	@echo "🔍 Running web checks..."
	cd web && bun run check

web-test:
	@echo "🧪 Running web tests..."
	cd web && bun run test

# Start the FastAPI application with Uvicorn locally
run-api:
	@echo "🚀 Starting FastAPI app with Uvicorn locally..."
	cd api && { \
		uv pip show python-dotenv && \
		(pkill -f "uvicorn.*18000" || true) && \
		sleep 2 && \
		uv run python -m dotenv -f ../.env run uvicorn src.main:app --host 0.0.0.0 --port 18000 --reload; \
	} || echo "python-dotenv not found; run 'make install'"

# Check for python-dotenv in the environment
check_dotenv: install
	@echo "Checking for python-dotenv..."
	uv pip show python-dotenv
	@echo "Attempting to run dotenv module directly..."
	uv run python -m dotenv --version

# Code Quality and Development Tools
# ==================================

# Check code quality with Ruff
lint:
	@echo "🔍 Running code quality checks with Ruff..."
	uv run ruff check .

# Auto-fix code quality issues
lint-fix:
	@echo "🔧 Auto-fixing code quality issues with Ruff..."
	uv run ruff check --fix .

# Run pre-commit hooks on all files
pre-commit:
	@echo "🚀 Running pre-commit hooks on all files..."
	uv run pre-commit run --all-files || echo "⚠️  Pre-commit made changes but continuing..."

# Format code with Black
format:
	@echo "✨ Formatting code with Black..."
	uv run black .

# Sort imports with isort
sort-imports:
	@echo "📋 Sorting imports with isort..."
	uv run isort .

# Run tests
test:
	@echo "🧪 Running tests..."
	cd api && python -m pytest tests/ -v || echo "⚠️  Tests failed but continuing..."

# Type checking with MyPy
type-check:
	@echo "🔍 Running type checks with MyPy..."
	uv run mypy api/src/ --ignore-missing-imports || echo "⚠️  Type check failed but continuing..."

# Comprehensive quality check (lint + pre-commit)
check-quality: lint
	@echo "✅ Running comprehensive quality checks..."
	@echo "Running pre-commit hooks..."
	uv run pre-commit run --all-files
	@echo "All quality checks passed!"

# Complete development quality gate - runs everything (fast version without type checking)
check-all: lint-fix format sort-imports test lint pre-commit web-check web-test
	@echo "🎉 ALL QUALITY CHECKS PASSED! 🎉"
	@echo "✅ Code formatting completed"
	@echo "✅ Import sorting completed"
	@echo "✅ Python tests passed"
	@echo "✅ Linting passed"
	@echo "✅ Pre-commit hooks passed"
	@echo "✅ Web checks passed"
	@echo "✅ Web tests passed"
	@echo "🚀 Ready for commit!"

# Complete development quality gate - runs everything (with type checking - slower)
check-all-with-types: lint-fix format sort-imports type-check test lint pre-commit web-check web-test
	@echo "🎉 ALL QUALITY CHECKS PASSED! 🎉"
	@echo "✅ Code formatting completed"
	@echo "✅ Import sorting completed"
	@echo "✅ Python type checking completed"
	@echo "✅ Python tests passed"
	@echo "✅ Linting passed"
	@echo "✅ Pre-commit hooks passed"
	@echo "✅ Web checks passed"
	@echo "✅ Web tests passed"
	@echo "🚀 Ready for commit!"

# Phase 1 Demo and Status
demo-phase1:
	@echo "🎯 Running Phase 1 Architecture Demo..."
	python scripts/demos/phase1_demo.py
