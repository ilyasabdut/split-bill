.PHONY: all venv install start clean

# Default target: install dependencies and start the app
all: start

# Create a virtual environment using uv
venv:
	@echo "Creating virtual environment with uv..."
	# You can specify the python interpreter for uv to use if needed:
	# uv venv -p python3.9  (or whatever version you intend)
	# For now, let's assume uv picks a suitable one or you manage it outside.
	uv venv -p python3.12

# Install dependencies from requirements.txt using uv
install: venv
	@echo "Installing dependencies with uv into .venv..."
	# Activate the venv in this subshell before running uv pip install
	. .venv/bin/activate && uv pip install -r requirements.txt && echo "Installation complete. Check for python-dotenv above."

# Start the Streamlit application
start: install
	@echo "Starting Streamlit app..."
	# Activate the venv and then explicitly use python from .venv
	. .venv/bin/activate && .venv/bin/python -m dotenv run -- streamlit run src/main.py

# Clean up the virtual environment
clean:
	@echo "Removing virtual environment..."
	rm -rf .venv
	@echo "Virtual environment removed."

check_dotenv: venv install # New target to specifically check dotenv
	@echo "Checking for python-dotenv in .venv..."
	. .venv/bin/activate && .venv/bin/python -m pip show python-dotenv && echo "python-dotenv found if listed above."
	@echo "Attempting to run dotenv module directly..."
	. .venv/bin/activate && .venv/bin/python -m dotenv --version && echo "dotenv module ran successfully if version shown."
