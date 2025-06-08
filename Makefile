.PHONY: all build up down logs clean rebuild-api rebuild-app install start run-api run-streamlit check_dotenv

# Default target: install dependencies and start the Streamlit app
all: start

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start services with Docker Compose
up:
	@echo "Starting services with Docker Compose..."
	docker-compose up --build -d

# Stop and remove Docker Compose services
down:
	@echo "Stopping and removing Docker Compose services..."
	docker-compose down

# Display logs for all services
logs:
	@echo "Displaying logs for all services (Ctrl+C to exit)..."
	docker-compose logs -f

# Clean up Docker images and volumes
clean:
	@echo "Cleaning up Docker images and volumes..."
	docker-compose down --volumes --rmi all
	docker volume prune -f
	docker image prune -a -f
	@echo "Cleanup complete."

# Helper for development: rebuild and restart a specific service
rebuild-api:
	@echo "Rebuilding and restarting API service..."
	docker-compose up --build -d api

rebuild-app:
	@echo "Rebuilding and restarting App service..."
	docker-compose up --build -d app

# Install dependencies using uv
install:
	@echo "Installing dependencies with uv..."
	uv pip show uv || uv pip install uv
	uv sync

# Start the Streamlit application locally
start: run-streamlit

run-streamlit:
	@echo "Starting Streamlit app locally..."
	uv pip show python-dotenv && \
	uv run python -m dotenv run -- streamlit run app/src/main.py || \
	echo "python-dotenv not found; run 'make install'"

# Start the FastAPI application with Uvicorn locally
run-api:
	@echo "Starting FastAPI app with Uvicorn locally..."
	cd api && { \
		uv pip show python-dotenv && \
		uv run python -m dotenv -f ../.env run uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload; \
	} || echo "python-dotenv not found; run 'make install'"

# Check for python-dotenv in the environment
check_dotenv: install
	@echo "Checking for python-dotenv..."
	uv pip show python-dotenv
	@echo "Attempting to run dotenv module directly..."
	uv run python -m dotenv --version
