.PHONY: all build up down logs clean rebuild-api rebuild-app venv install start run-api run-streamlit check_dotenv

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

# --- Local Development Commands (using uv) ---
# Create a virtual environment using uv
venv:
	@echo "Creating virtual environment with uv..."
	uv venv -p python3.12

# Install dependencies from requirements.txt using uv
install: venv
	@echo "Installing dependencies with uv into .venv..."
	. .venv/bin/activate && uv pip install -r requirements.txt && echo "Installation complete."

# Start the Streamlit application locally
start: run-streamlit

run-streamlit: install
	@echo "Starting Streamlit app locally..."
	. .venv/bin/activate && .venv/bin/python -m dotenv run -- streamlit run app/main.py

# Start the FastAPI application with Uvicorn locally
run-api: install
	@echo "Starting FastAPI app with Uvicorn locally..."
	# Change directory to 'api/' before running uvicorn so it can find sibling modules
	cd api && . ../.venv/bin/activate && . ../.venv/bin/python -m dotenv run -- uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# New target to specifically check dotenv (kept from user's provided Makefile)
check_dotenv: venv install
	@echo "Checking for python-dotenv in .venv..."
	. .venv/bin/activate && .venv/bin/python -m pip show python-dotenv && echo "python-dotenv found if listed above."
	@echo "Attempting to run dotenv module directly..."
	. .venv/bin/activate && .venv/bin/python -m dotenv --version && echo "dotenv module ran successfully if version shown."
