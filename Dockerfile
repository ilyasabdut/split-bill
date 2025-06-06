# syntax=docker/dockerfile:1.4

# --- Builder Stage ---
FROM python:3.12-slim as builder

WORKDIR /opt/app

# Install uv (ultra fast pip alternative)
RUN pip install --no-cache-dir uv
COPY requirements.txt .

# Create a virtual environment and install dependencies using uv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --no-cache-dir -r requirements.txt

# --- Final Stage ---
FROM python:3.12-slim as final

WORKDIR /app

# Create src directory
RUN mkdir src

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY ./app/src/main.py /app/src/
COPY .streamlit/ .streamlit/
COPY ./api/src /app/src

# Expose both ports
EXPOSE 8501 8000

# Add /app to Python path
ENV PYTHONPATH=/app

# Set the activate path for the venv
ENV PATH="/opt/venv/bin:$PATH"

# Environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Healthcheck for Streamlit
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Healthcheck for FastAPI
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command to run the Streamlit app
CMD ["streamlit", "run", "/app/src/main.py"]

# Uncomment the following line to run the FastAPI app instead
# CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--http", "httptools"]
