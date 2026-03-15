# ADR-003: Garage for Object Storage

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
- Low resource requirements

## Decision

We chose **Garage** as our object storage solution.

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
- Higher resource requirements than Garage

**Verdict**: Rejected - Garage offers better efficiency for our needs

### 4. Garage

**Pros**:
- S3-compatible API (drop-in replacement)
- Self-hosted (data privacy, no egress costs)
- Docker-native
- Very lightweight (single binary)
- Low resource requirements (1GB RAM)
- Distributed by design (data replicated in 3 zones)
- Highly resilient to network failures
- Open source

**Cons**:
- Self-managed (ops overhead)
- Smaller community than MinIO
- Newer project

**Verdict**: **Accepted** - Best balance of features, efficiency, and control

## Consequences

### Positive

1. **S3 Compatibility**: Works with existing S3 libraries and tools
2. **Cost**: No per-request or egress fees
3. **Privacy**: Data stays in our infrastructure
4. **Efficiency**: Very low resource requirements (1GB RAM)
5. **Resilience**: Data automatically replicated across zones
6. **Development**: Same code works locally and in production
7. **Backup**: Simple file-based backups
8. **Deployment**: Single dependency-free binary

### Negative

1. **Operations**: Need to monitor and maintain Garage instance
2. **Storage**: Requires persistent disk space
3. **Learning Curve**: S3 API concepts for team

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
# Garage S3 client configuration (using minio library)
storage_client = Minio(
    "garage:3900",
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False  # True in production with SSL
)

# Ensure bucket exists
if not storage_client.bucket_exists("split-bill"):
    storage_client.make_bucket("split-bill")
```

### Image Storage Flow

1. User uploads receipt image
2. Image is compressed (reduce size for OCR)
3. Image is stored in Garage: `receipts/{split_id}.jpg`
4. Metadata stored: `metadata/{split_id}.json`
5. Share link generated pointing to Garage data

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
  garage:
    image: dxflrs/garage:latest
    ports:
      - "3900:3900"   # S3 API port
      - "3902:3902"   # Admin web UI
    environment:
      GARAGE_RPC_SECRET: changeme
      GARAGE_ADMIN_TOKEN: admin_token_change_me
      GARAGE_S3_API_REGION: garage
    volumes:
      - garage_data:/data
      - garage_meta:/meta
    command: >
      /garage
      --config /etc/garage/config.toml
      server

volumes:
  garage_data:
  garage_meta:
```

### Security Considerations

1. **Access Keys**: Use environment variables, never hardcode
2. **Bucket Policies**: Restrict public access
3. **Presigned URLs**: Use for temporary access (viewing receipts)
4. **SSL/TLS**: Enable in production
5. **Backup**: Regular snapshots of Garage data volumes
6. **RPC Secret**: Use strong secret for cluster communication

## Migration Path

If we need to migrate to AWS S3 later:

1. Garage and S3 use same API (boto3/minio libraries)
2. Only endpoint and credentials change
3. Data migration via `mc mirror` or `rclone`
4. Zero code changes required

## Performance

- **Upload**: ~100ms for 1MB image (local network)
- **Download**: ~50ms for 1MB image (cached)
- **Storage**: ~2MB per receipt (compressed)

## Resource Requirements

- **CPU**: Any x86_64 from last 10 years, ARMv7/v8
- **RAM**: 1 GB minimum
- **Disk**: At least 16 GB
- **Network**: 200ms latency or less, 50 Mbps or more

## Future Considerations

- **Multi-zone deployment**: Deploy Garage across multiple datacenters
- **Lifecycle Policies**: Auto-delete old receipts after X days
- **Versioning**: Enable for data protection
- **Monitoring**: Implement health checks for Garage cluster

## Related Decisions

- ADR-007: Docker for Containerization
- ADR-002: Redis for Caching

## References

- [Garage Documentation](https://garagehq.deuxfleurs.fr/documentation/)
- [S3 API Compatibility](https://garagehq.deuxfleurs.fr/documentation/connect/s3/)
- [Garage Docker Hub](https://hub.docker.com/r/dxflrs/garage)
- [Garage Source Code](https://git.deuxfleurs.fr/Deuxfleurs/garage)
