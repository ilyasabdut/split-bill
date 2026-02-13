# Docker Compose Updates

## Changes Made

### 1. Added MinIO Service to Docker Compose Files

Both `docker/docker-compose.yml` and `docker/docker-compose.prod.yml` were missing the MinIO service despite having MinIO environment variables configured for the API service.

**Added MinIO service configuration:**
```yaml
minio:
  image: minio/minio:latest
  container_name: split-bill-minio
  ports:
    - "9000:9000"  # API port
    - "9001:9001"  # Console port
  environment:
    MINIO_ROOT_USER: ${MINIO_ACCESS_KEY:-minioadmin}
    MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY:-minioadmin}
  volumes:
    - minio_data:/data
  command: server /data --console-address ":9001"
  restart: unless-stopped
```

### 2. Updated Volumes Section

Added `minio_data` volume to both compose files:
```yaml
volumes:
  redis_data:
  minio_data:
```

### 3. Updated Makefile Help Text

Clarified that `make start` is an alias for `make web-dev` to avoid confusion about duplicate commands.

## Why MinIO is Needed

MinIO provides object storage for:
- Receipt image uploads
- OCR processing
- Persistent storage of split data
- Shareable links with images

## Services Now Included

1. **Web** (SvelteKit frontend) - Port 15173
2. **API** (FastAPI backend) - Port 18000
3. **Redis** (Caching) - Port 16379
4. **MinIO** (Object storage) - Ports 9000 (API) & 9001 (Console)

## Environment Variables Required

```bash
# MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=split-bill
MINIO_USE_SSL=False
```

## Accessing MinIO

- API Endpoint: http://localhost:9000
- Web Console: http://localhost:9001
- Default credentials: minioadmin/minioadmin

## Next Steps

1. Ensure MinIO bucket is created on startup
2. Configure proper access policies
3. Set up secure credentials in production
