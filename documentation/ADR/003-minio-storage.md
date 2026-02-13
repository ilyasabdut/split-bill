# ADR-003: MinIO for Object Storage

## Status

**Accepted** - Implemented and in production

## Context

We need persistent storage for:
1. Receipt images (uploaded by users)
2. Split calculation metadata (JSON files)
3. Share link data (for viewing splits later)

Requirements:
- Object storage (images + JSON files)
- S3-compatible API
- Self-hosted option (privacy, cost)
- Docker-friendly
- Easy to backup and migrate

## Decision

We chose **MinIO** as our object storage solution.

## Alternatives Considered

### 1. Local Filesystem

**Pros**:
- Simplest implementation
- No external dependencies
- Direct file access

**Cons**:
- Hard to scale horizontally
- No built-in redundancy
- Backup/restore complexity
- File permissions management
- Sharing across containers difficult

**Verdict**: Rejected - Not suitable for production deployment

### 2. Amazon S3

**Pros**:
- Industry standard
- Highly reliable (99.999999999% durability)
- Global CDN (CloudFront)
- Managed service (no ops overhead)
- Pay-as-you-go

**Cons**:
- Ongoing cost (storage + egress)
- Data leaves our infrastructure
- Requires AWS account
- Complex pricing model
- Latency for non-AWS deployments

**Verdict**: Rejected - Cost and data privacy concerns for self-hosted option

### 3. MinIO

**Pros**:
- S3-compatible API (drop-in replacement)
- Self-hosted (data privacy, no egress costs)
- Docker-native
- High performance
- Erasure coding for data protection
- Simple deployment
- Open source

**Cons**:
- Self-managed (ops overhead)
- Single-node deployment not highly available
- Requires persistent storage

**Verdict**: **Accepted** - Best balance of features and control

## Consequences

### Positive

1. **S3 Compatibility**: Works with existing S3 libraries and tools
2. **Cost**: No per-request or egress fees
3. **Privacy**: Data stays in our infrastructure
4. **Flexibility**: Can migrate to AWS S3 later if needed
5. **Development**: Same code works locally and in production
6. **Backup**: Simple file-based backups

### Negative

1. **Operations**: Need to monitor and maintain MinIO instance
2. **Storage**: Requires persistent disk space
3. **Single Point of Failure**: Single-node deployment
4. **Learning Curve**: S3 API concepts for team

## Implementation Details

### Data Organization

```
bucket: split-bill
├── receipts/
│   └── {split_id}.jpg          # Original receipt images
└── metadata/
    └── {split_id}.json         # Split calculation data
```

### Storage Structure

```python
# MinIO client configuration
minio_client = Minio(
    "minio:9000",
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False  # True in production with SSL
)

# Ensure bucket exists
if not minio_client.bucket_exists("split-bill"):
    minio_client.make_bucket("split-bill")
```

### Image Storage Flow

1. User uploads receipt image
2. Image is compressed (reduce size for OCR)
3. Image is stored in MinIO: `receipts/{split_id}.jpg`
4. Metadata stored: `metadata/{split_id}.json`
5. Share link generated pointing to MinIO data

### Metadata Format

```json
{
    "split_id": "abc123def456",
    "original_parsed_data": {
        "items": [...],
        "subtotal": 46.98,
        "tax": 4.23,
        "total": 51.21
    },
    "person_names": ["Alice", "Bob"],
    "item_assignments": [...],
    "calculated_split_results": {...},
    "creation_timestamp": 1735689600.0
}
```

### Docker Configuration

```yaml
# docker-compose.yml
services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"   # API port
      - "9001:9001"   # Console port
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

volumes:
  minio_data:
```

### Security Considerations

1. **Access Keys**: Use environment variables, never hardcode
2. **Bucket Policies**: Restrict public access
3. **Presigned URLs**: Use for temporary access (viewing receipts)
4. **SSL/TLS**: Enable in production
5. **Backup**: Regular snapshots of MinIO data volume

## Migration Path

If we need to migrate to AWS S3 later:

1. MinIO and S3 use same API (boto3/minio libraries)
2. Only endpoint and credentials change
3. Data migration via `mc mirror` or `rclone`
4. Zero code changes required

## Performance

- **Upload**: ~100ms for 1MB image (local network)
- **Download**: ~50ms for 1MB image (cached)
- **Storage**: ~2MB per receipt (compressed)

## Future Considerations

- **Erasure Coding**: Enable for data protection (minio server with erasure sets)
- **Distributed Mode**: Run MinIO in distributed mode for HA
- **Lifecycle Policies**: Auto-delete old receipts after X days
- **Versioning**: Enable for data protection

## Related Decisions

- ADR-007: Docker for Containerization
- ADR-002: Redis for Caching

## References

- [MinIO Documentation](https://docs.min.io/)
- [S3 API Compatibility](https://docs.min.io/docs/minio-client-complete-guide)
- [MinIO Docker Hub](https://hub.docker.com/r/minio/minio/)
