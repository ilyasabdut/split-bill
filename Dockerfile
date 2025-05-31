# syntax=docker/dockerfile:1.4

# --- Builder Stage ---
FROM python:3.12-slim as builder

WORKDIR /opt/app

# Install build dependencies (if any, though for these packages usually not much beyond pip)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Create a virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# --- Final Stage ---
FROM python:3.12-slim as final

WORKDIR /app

# Create src directory
RUN mkdir src

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code into src
COPY /app/src/main.py /app/src/
COPY .streamlit/ .streamlit/

# Make port 8501 available to the world outside this container (Streamlit default)
EXPOSE 8501

# Set the activate path for the venv
ENV PATH="/opt/venv/bin:$PATH"
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0 
# Ensures Streamlit listens on all interfaces inside the container

# Healthcheck (optional but good practice)
# Streamlit has a built-in health check at /healthz
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Default command to run the app
CMD ["streamlit", "run", "/app/src/main.py"]
