.PHONY: all venv install start clean

# Default target: install dependencies and start the app
all: start

# Create a virtual environment using uv
venv:
	@echo "Creating virtual environment with uv..."
	uv venv

# Install dependencies from requirements.txt using uv
install: venv
	@echo "Installing dependencies with uv..."
	uv pip install -r requirements.txt

# Start the Streamlit application
start: install
	@echo "Starting Streamlit app..."
	# Ensure the virtual environment is activated before running streamlit
	. .venv/bin/activate && streamlit run main.py

# Clean up the virtual environment
clean:
	@echo "Removing virtual environment..."
	rm -rf .venv

