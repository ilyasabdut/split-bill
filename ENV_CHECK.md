# Environment Configuration Check

## Current Status

### ❌ Your `.env` file is INCOMPLETE
Your current `.env` file only contains:
```bash
API_KEY=test-key-123
```

### ✀️ Required Environment Variables

Based on the application architecture, you need the following environment variables:

## API Backend Requirements

| Variable | Description | Current Value | Required? |
|----------|-------------|---------------|-----------|
| `API_KEY` | API authentication key | `test-key-123` | ✅ Yes |
| `APP_BASE_URL` | Base URL for the application | Missing | ⚠️ Recommended |
| `OPENROUTER_API_KEY` | OCR service API key | Missing | ⚠️ For OCR features |
| `OPENROUTER_MODEL_NAME` | OCR model name | Missing | ❌ Optional |
| `MINIO_ENDPOINT` | MinIO server endpoint | Missing | ✅ Yes |
| `MINIO_ACCESS_KEY` | MinIO access key | Missing | ✅ Yes |
| `MINIO_SECRET_KEY` | MinIO secret key | Missing | ✅ Yes |
| `MINIO_BUCKET_NAME` | MinIO bucket name | Missing | ✅ Yes |
| `MINIO_USE_SSL` | Use SSL for MinIO | Missing | ❌ Optional |
| `REDIS_URL` | Redis connection URL | Missing | ✅ Yes |

## Web Frontend Requirements

| Variable | Description | Current Value | Required? |
|----------|-------------|---------------|-----------|
| `VITE_FASTAPI_API_URL` | FastAPI backend URL | Missing | ✅ Yes |
| `VITE_API_KEY` | API key for frontend | Missing | ✅ Yes |

## Quick Fix

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Or use the local config:**
   ```bash
   cp .env.local .env
   ```

3. **Update the values:**
   - Set your actual API keys
   - Configure MinIO credentials
   - Set up OpenRouter API key for OCR

## Local Development Setup

For local development, you can use these defaults:

```bash
# API Configuration
API_KEY=test-key-123

# Backend URLs
FASTAPI_API_URL=http://localhost:18000
APP_BASE_URL=http://localhost:15173

# OpenRouter OCR (get from openrouter.ai)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL_NAME=mistralai/mistral-small-3.2-24b-instruct:free

# MinIO Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=split-bill
MINIO_USE_SSL=False

# Redis Cache
REDIS_URL=redis://localhost:6379

# Frontend Configuration
VITE_FASTAPI_API_URL=http://localhost:18000
VITE_API_KEY=test-key-123
```

## Services Required

1. **Redis** - Running on port 6379 (or 16379 via Docker)
2. **MinIO** - Running on port 9000 (API) and 9001 (Console)
3. **FastAPI** - Running on port 18000
4. **SvelteKit** - Running on port 15173

## Next Steps

1. Update your `.env` file with the complete configuration
2. Ensure all services are running
3. Test the application functionality

## Files Created

- `.env.local` - Complete local development configuration
- This check document for reference
