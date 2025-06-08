# syntax=docker/dockerfile:1.4

FROM python:3.12-slim as builder

WORKDIR /opt/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tar gcc libjpeg-dev libpng-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv binary globally (optional, won't be used for Streamlit)
RUN curl -L https://github.com/astral-sh/uv/releases/latest/download/uv-aarch64-unknown-linux-gnu.tar.gz \
    | tar -xz && mv uv-aarch64-unknown-linux-gnu/uv /usr/local/bin/uv && chmod +x /usr/local/bin/uv

# Upgrade pip and install dependencies globally
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir streamlit pandas requests Pillow

# Cleanup
RUN rm -rf /root/.cache/pip && \
    apt-get purge -y --auto-remove gcc && \
    find /usr/local/lib/python3.12/site-packages -name '*.pyc' -delete && \
    find /usr/local/lib/python3.12/site-packages -name '__pycache__' -delete && \
    rm -rf /usr/local/lib/python3.12/site-packages/*/tests

# --- Final image ---
FROM python:3.12-slim as final

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv

COPY /app/src/ /app/src/
COPY .streamlit/ .streamlit/

ENV PATH="/usr/local/bin:$PATH"
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

CMD ["python", "-m", "streamlit", "run", "/app/src/main.py"]
