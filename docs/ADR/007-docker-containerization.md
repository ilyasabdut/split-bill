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

## Implementation

See `docker/docker-compose.yml` (web, api, postgres), `docker/Dockerfile.web` and `docker/Dockerfile.api`. Day-to-day commands are the `make up` / `down` / `logs` targets.

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

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [12-Factor App](https://12factor.net/)
