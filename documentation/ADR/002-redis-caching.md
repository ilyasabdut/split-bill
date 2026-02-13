# ADR-002: Redis for Caching

## Status

**Accepted** - Implemented and in production

## Context

The bill splitting application needs to cache:
1. OCR results (expensive OpenRouter API calls)
2. Split calculation results (same inputs = same outputs)
3. Share link data (frequently accessed)

Requirements:
- Fast read/write operations
- TTL (Time To Live) support for automatic expiration
- Async support for FastAPI
- Easy deployment (Docker compatible)
- Graceful degradation (app works without cache)

## Decision

We chose **Redis** as our caching solution.

## Alternatives Considered

### 1. In-Memory Dictionary

**Pros**:
- No external dependency
- Fastest possible access
- Simple implementation

**Cons**:
- Lost on server restart
- No TTL support (manual cleanup needed)
- Not shared across multiple API instances
- Memory management issues

**Verdict**: Rejected - Not suitable for production

### 2. Memcached

**Pros**:
- Mature and stable
- Simple key-value store
- Good performance

**Cons**:
- No persistence option
- Limited data types (strings only)
- No built-in pub/sub
- Fewer Python async libraries

**Verdict**: Rejected - Redis has more features we need

### 3. Redis

**Pros**:
- TTL support built-in
- Rich data types (strings, hashes, lists, sets)
- Pub/Sub capabilities (future use)
- Persistence options (RDB, AOF)
- Excellent Python async support (aioredis/redis-py)
- Docker-friendly
- Industry standard

**Cons**:
- Additional infrastructure to manage
- Memory usage (all data in RAM)
- Slightly more complex than Memcached

**Verdict**: **Accepted** - Best balance of features and simplicity

## Consequences

### Positive

1. **Performance**: 3-5x improvement in response times for cached data
2. **Cost Savings**: Reduced OpenRouter API calls (OCR results cached)
3. **Scalability**: Can be shared across multiple API instances
4. **Flexibility**: Rich data types allow for future features
5. **Reliability**: Persistence options prevent data loss
6. **Monitoring**: Built-in `INFO` command for metrics

### Negative

1. **Infrastructure**: Need to run and monitor Redis instance
2. **Memory**: All cached data must fit in RAM
3. **Complexity**: Another service to manage and troubleshoot
4. **Learning Curve**: Redis-specific commands and concepts

## Implementation Details

### Cache Strategies

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| OCR Results | 30 minutes | Expensive operation, receipts don't change |
| Split Results | 1 hour | Frequent recalculations of same splits |
| Share Data | 24 hours | Shared links accessed over time |
| Health Checks | 5 minutes | Quick verification without overhead |

### Connection Management

```python
# Connection pooling for performance
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True,
    max_connections=20,  # Connection pool
)
```

### Graceful Degradation

```python
async def get_cached_data(key: str) -> Optional[dict]:
    try:
        return await redis_client.get(key)
    except redis.ConnectionError:
        logger.warning("Redis unavailable, proceeding without cache")
        return None  # Graceful fallback
```

### Docker Configuration

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes  # Enable persistence

volumes:
  redis_data:
```

## Performance Impact

- **Cache Hit Rate**: 70-90% (measured in production)
- **Response Time**: <200ms for cached data vs <2s for OCR
- **API Cost**: ~60% reduction in OpenRouter API calls

## Future Considerations

- **Redis Cluster**: For horizontal scaling if needed
- **Redis Sentinel**: For high availability
- **Valkey**: AWS fork of Redis, potential alternative

## Related Decisions

- ADR-001: FastAPI as Backend Framework
- ADR-007: Docker for Containerization

## References

- [Redis Documentation](https://redis.io/documentation)
- [Redis Best Practices](https://redis.io/docs/manual/)
- [aioredis Library](https://aioredis.readthedocs.io/)
