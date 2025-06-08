# syntax=docker/dockerfile:1.4

# --- Builder Stage ---
FROM python:3.12-slim as builder

WORKDIR /opt/app

# Install curl, ca-certificates, and tar for downloading and extracting uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tar && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install uv (replace with appropriate arch if needed)
RUN curl -L https://github.com/astral-sh/uv/releases/latest/download/uv-aarch64-unknown-linux-gnu.tar.gz \
    | tar -xz && mv uv /opt/venv/bin/uv

    # Copy dependency files
COPY pyproject.toml .
COPY uv.lock .

# Sync dependencies using uv
RUN uv sync


# --- Final Stage ---
FROM python:3.12-slim as final

WORKDIR /app

# Create src directory
RUN mkdir -p /app/src

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code and Streamlit config
COPY /app/src/main.py /app/src/
COPY .streamlit/ .streamlit/

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Set up environment
ENV PATH="/opt/venv/bin:$PATH"
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Healthcheck for Streamlit
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Default command
CMD ["streamlit", "run", "/app/src/main.py"]
