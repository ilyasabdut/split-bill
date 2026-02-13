# ADR-007: Docker for Containerization

## Status

**Accepted** - Implemented and in production

## Context

We need to:
1. Consistent development environment across team
2. Easy deployment to various environments (dev, staging, prod)
3. Isolate dependencies (Python versions, system packages)
4. Simplify onboarding for new developers
5. Support multiple services (frontend, backend, cache, storage)

## Decision

We chose **Docker** with Docker Compose for containerization.

## Alternatives Considered

### 1. Virtual Environments (venv/poetry)

**Pros**:
- Simple for single Python app
- Native Python tooling
- Fast startup

**Cons**:
- System dependencies still required
- "Works on my machine" issues
- Hard to replicate exact environment
- No service orchestration

**Verdict**: Rejected - Insufficient for multi-service architecture

### 2. Virtual Machines

**Pros**:
- Full isolation
- Can run different OS
- Mature technology

**Cons**:
- Heavy resource usage
- Slow startup
- Complex management
- Overkill for microservices

**Verdict**: Rejected - Too heavy for our use case

### 3. Docker

**Pros**:
- Lightweight containers
- Fast startup
- Consistent environments
- Great ecosystem (Docker Hub)
- Easy orchestration with Compose
- Industry standard
- Works everywhere (dev, CI, prod)

**Cons**:
- Learning curve for team
- Image size management needed
- Security considerations
- Additional tooling

**Verdict**: **Accepted** - Best fit for our requirements

### 4. Kubernetes

**Pros**:
- Production-grade orchestration
- Auto-scaling
- Self-healing
- Industry standard for large deployments

**Cons**:
- Overkill for our scale
- Complex to set up and manage
- Steep learning curve
- Requires dedicated ops expertise

**Verdict**: Rejected - Too complex for current needs

## Consequences

### Positive

1. **Consistency**: Same environment from dev to production
2. **Isolation**: Each service in its own container
3. **Portability**: Run anywhere Docker is supported
4. **Scalability**: Easy to add more instances later
5. **Version Control**: Infrastructure as code (Dockerfiles)
6. **Onboarding**: New devs run `docker-compose up`
7. **Testing**: Spin up full stack for integration tests

### Negative

1. **Complexity**: Additional layer to understand
2. **Resources**: Containers use memory/CPU
3. **Networking**: Need to understand container networking
4. **Debugging**: Harder to debug inside containers
5. **Storage**: Volume management needed for persistence

## Implementation Details

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                Docker Compose Stack                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │   Streamlit  │  │   FastAPI    │                │
│  │   (app)      │  │   (api)      │                │
│  │   Port 8501  │  │   Port 8000  │                │
│  └──────┬───────┘  └──────┬───────┘                │
│         │                 │                         │
│         └────────┬────────┘                         │
│                  │                                  │
│         ┌────────▼────────┐                        │
│         │     Redis       │                        │
│         │   (Port 6379)   │                        │
│         └─────────────────┘                        │
│                  │                                  │
│         ┌────────▼────────┐                        │
│         │     MinIO       │                        │
│         │   (Port 9000)   │                        │
│         └─────────────────┘                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Dockerfile - Frontend (Streamlit)

```dockerfile
# docker/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir streamlit

# Copy application code
COPY app/ ./app/

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app/src/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false"]
```

### Dockerfile - Backend (FastAPI)

```dockerfile
# docker/Dockerfile.api
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY api/ ./api/

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Uvicorn
CMD ["uvicorn", "api.src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload"]
```

### Docker Compose - Development

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8501:8501"
    environment:
      - API_KEY=${API_KEY}
      - FASTAPI_API_URL=http://api:8000
    depends_on:
      - api
    volumes:
      - ../app:/app/app  # Hot reload
    networks:
      - split-bill-network

  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - API_KEY=${API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
    depends_on:
      - redis
      - minio
    volumes:
      - ../api:/app/api  # Hot reload
    networks:
      - split-bill-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - split-bill-network

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    networks:
      - split-bill-network

volumes:
  redis_data:
  minio_data:

networks:
  split-bill-network:
    driver: bridge
```

### Docker Compose - Production

```yaml
# docker/docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    restart: always
    environment:
      - API_KEY=${API_KEY}
      - FASTAPI_API_URL=http://api:8000
    depends_on:
      - api
    networks:
      - split-bill-network

  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile.api
    restart: always
    environment:
      - API_KEY=${API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - REDIS_URL=redis://redis:6379
      - MINIO_ENDPOINT=minio:9000
    deploy:
      replicas: 2  # Scale API horizontally
    depends_on:
      - redis
      - minio
    networks:
      - split-bill-network

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - split-bill-network

  minio:
    image: minio/minio:latest
    restart: always
    volumes:
      - minio_data:/data
    command: server /data
    networks:
      - split-bill-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
      - api
    networks:
      - split-bill-network

volumes:
  redis_data:
  minio_data:

networks:
  split-bill-network:
    driver: bridge
```

## Development Workflow

### Start All Services
```bash
docker-compose -f docker/docker-compose.yml up --build
```

### Start Specific Service
```bash
docker-compose -f docker/docker-compose.yml up api
```

### View Logs
```bash
docker-compose -f docker/docker-compose.yml logs -f api
```

### Run Commands in Container
```bash
docker-compose -f docker/docker-compose.yml exec api bash
```

### Stop Everything
```bash
docker-compose -f docker/docker-compose.yml down
```

### Clean Up
```bash
docker-compose -f docker/docker-compose.yml down -v --rmi all
```

## Best Practices

1. **Multi-stage Builds**: Separate build and runtime stages
2. **Non-root User**: Run containers as non-root
3. **Health Checks**: Verify services are healthy
4. **Resource Limits**: Set memory/CPU limits
5. **Layer Caching**: Order Dockerfile commands for cache efficiency
6. **Secrets**: Use environment variables, never commit secrets
7. **Volumes**: Persist data outside containers

## Production Considerations

- Use orchestration (Swarm/Kubernetes) for high availability
- Implement proper secret management (Docker Secrets, Vault)
- Set up log aggregation (ELK stack, Datadog)
- Monitor container health and resource usage
- Implement rolling updates
- Use private registry for images

## Related Decisions

- ADR-001: FastAPI for backend
- ADR-004: Streamlit for frontend
- ADR-002: Redis for caching
- ADR-003: MinIO for storage

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [12-Factor App](https://12factor.net/)
