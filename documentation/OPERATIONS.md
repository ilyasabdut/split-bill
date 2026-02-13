# Operations Guide

## Overview

This guide covers deployment, monitoring, and operational aspects of the Split Bill application.

**Version**: 2.0.0
**Last Updated**: February 2026

---

## Table of Contents

- [Deployment](#deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)
- [Security](#security)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## Deployment

### Prerequisites

- Server with Docker and Docker Compose installed
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- Minimum 2GB RAM, 1 CPU core
- 10GB disk space

### Deployment Environments

```
Development → Staging → Production
```

### Production Deployment

#### Option 1: Docker Compose (Single Server)

**Step 1: Prepare Server**

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
 curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Step 2: Clone and Configure**

```bash
# Clone repository
git clone <repository-url> /opt/split-bill
cd /opt/split-bill

# Create production environment file
cp .env.example .env.production
nano .env.production
```

**Production Environment Variables**:

```bash
# Security (CRITICAL: Change from defaults!)
API_KEY=your-very-secure-random-key-min-32-chars

# OCR Service
OPENROUTER_API_KEY=your-openrouter-production-key
OPENROUTER_MODEL_NAME=anthropic/claude-3-sonnet-20240229

# URLs (Use your actual domain)
APP_BASE_URL=https://splitbill.yourdomain.com
FASTAPI_API_URL=https://api.splitbill.yourdomain.com

# Storage (Use strong passwords)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=your-secure-access-key
MINIO_SECRET_KEY=your-secure-secret-key-min-16-chars
MINIO_BUCKET_NAME=split-bill
MINIO_USE_SSL=False

# Redis (Optional password)
REDIS_URL=redis://:your-redis-password@redis:6379
```

**Step 3: Deploy**

```bash
# Pull latest images
docker-compose -f docker/docker-compose.prod.yml pull

# Start services
docker-compose -f docker/docker-compose.prod.yml up -d

# Verify
 docker-compose -f docker/docker-compose.prod.yml ps
docker-compose -f docker/docker-compose.prod.yml logs -f
```

**Step 4: Setup Reverse Proxy (Nginx)**

Create `/etc/nginx/sites-available/split-bill`:

```nginx
# Frontend (Streamlit)
server {
    listen 80;
    server_name splitbill.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.splitbill.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=api_limit burst=10 nodelay;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/split-bill /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Step 5: SSL with Let's Encrypt**

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificates
sudo certbot --nginx -d splitbill.yourdomain.com -d api.splitbill.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

#### Option 2: Cloud Deployment (AWS/GCP/Azure)

**AWS ECS/Fargate Example**:

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name split-bill

# Create task definition (save as task-definition.json)
{
    "family": "split-bill",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "containerDefinitions": [
        {
            "name": "api",
            "image": "your-registry/split-bill-api:latest",
            "portMappings": [{"containerPort": 8000}],
            "environment": [
                {"name": "API_KEY", "value": "your-key"}
            ]
        }
    ]
}

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### Option 3: Kubernetes

**Deployment Manifest** (`k8s/deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: split-bill-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: split-bill-api
  template:
    metadata:
      labels:
        app: split-bill-api
    spec:
      containers:
      - name: api
        image: split-bill-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: split-bill-secrets
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: split-bill-api-service
spec:
  selector:
    app: split-bill-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods
kubectl get svc
```

### Deployment Checklist

Before going live:

- [ ] Change default API key
- [ ] Enable HTTPS
- [ ] Configure firewall (only 80, 443 open)
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test health endpoints
- [ ] Verify rate limiting works
- [ ] Check SSL certificate auto-renewal
- [ ] Set up log rotation
- [ ] Document deployment process

---

## Configuration

### Environment Variables Reference

#### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `API_KEY` | API authentication key | `sk-abc123...` |
| `OPENROUTER_API_KEY` | OpenRouter API access | `sk-or-v1-...` |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |

#### Application

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_BASE_URL` | Frontend base URL | `http://localhost:8501` |
| `FASTAPI_API_URL` | API base URL | `http://localhost:8000` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |

#### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_MODEL_NAME` | OCR model | `mistralai/mistral-small-3.2-24b-instruct:free` |
| `OPENROUTER_HTTP_REFERER` | API referer header | - |
| `OPENROUTER_X_TITLE` | API title header | - |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment name | `development` |

### Configuration Files

#### Docker Compose Override

Create `docker-compose.override.yml` for local customization:

```yaml
version: '3.8'
services:
  api:
    volumes:
      - ./local-config:/app/config
    environment:
      - DEBUG=true
```

#### Nginx Configuration

Production nginx with security headers:

```nginx
server {
    listen 443 ssl http2;
    server_name api.splitbill.yourdomain.com;

    # SSL
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        limit_req zone=api_limit burst=20 nodelay;
    }
}
```

---

## Monitoring

### Health Checks

**Endpoint**: `GET /health`

Check application health:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.splitbill.yourdomain.com/health
```

Expected response:
```json
{
    "status": "healthy",
    "timestamp": 1735689600.0,
    "version": "2.0.0",
    "caching": "enabled",
    "cache": "connected"
}
```

### Metrics

**Endpoint**: `GET /metrics`

Monitor key metrics:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.splitbill.yourdomain.com/metrics
```

### Logging

#### View Logs

```bash
# Docker Compose
docker-compose -f docker/docker-compose.prod.yml logs -f api

# Specific time range
docker-compose logs --since="2026-02-11T10:00:00" api

# Tail last 100 lines
docker-compose logs --tail=100 api
```

#### Structured Logging

Logs are in JSON format for easy parsing:

```json
{
    "timestamp": "2026-02-11T10:30:00Z",
    "level": "INFO",
    "logger": "main",
    "message": "Split calculated",
    "request_id": "uuid",
    "endpoint": "/splits/calculate",
    "duration_ms": 150
}
```

#### Log Aggregation

Setup with Fluentd/Elasticsearch:

```yaml
# docker-compose.logging.yml
services:
  fluentd:
    image: fluent/fluentd
    volumes:
      - ./fluentd.conf:/fluentd/etc/fluent.conf

  elasticsearch:
    image: elasticsearch:8.x
    environment:
      - discovery.type=single-node

  kibana:
    image: kibana:8.x
    ports:
      - "5601:5601"
```

### Alerting

#### Prometheus + Alertmanager

```yaml
# prometheus/alerts.yml
groups:
- name: split-bill
  rules:
  - alert: HighErrorRate
    expr: rate(api_errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"

  - alert: ServiceDown
    expr: up{job="split-bill"} == 0
    for: 1m
    labels:
      severity: critical
```

#### Uptime Monitoring

Use external services:
- **UptimeRobot**: Free tier, 5-minute checks
- **Pingdom**: Paid, more features
- **StatusCake**: Free tier available

Setup health check endpoint:
```bash
# UptimeRobot monitor
URL: https://api.splitbill.yourdomain.com/health
Interval: 5 minutes
Expected response: HTTP 200
```

---

## Backup & Recovery

### What to Backup

1. **MinIO Data**: Receipt images and metadata
2. **Redis Data**: Cache (optional, can be rebuilt)
3. **Environment Configuration**: .env files
4. **Code**: Git repository

### Backup Strategy

#### Automated Backups (Daily)

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/split-bill/$DATE"
mkdir -p $BACKUP_DIR

# Backup MinIO
docker run --rm -v split-bill_minio_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/minio.tar.gz -C /data .

# Backup Redis (if persistence enabled)
docker run --rm -v split-bill_redis_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/redis.tar.gz -C /data .

# Sync to S3 (optional)
aws s3 sync $BACKUP_DIR s3://your-backup-bucket/split-bill/$DATE/

# Keep only last 7 days
find /backup/split-bill -type d -mtime +7 -exec rm -rf {} +
```

Add to crontab:
```bash
# Daily at 2 AM
0 2 * * * /opt/split-bill/scripts/backup.sh >> /var/log/backup.log 2>&1
```

#### Manual Backup

```bash
# MinIO
docker-compose -f docker/docker-compose.prod.yml exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker-compose exec minio mc mirror local/split-bill /backup/minio

# Complete stack
docker-compose -f docker/docker-compose.prod.yml down
tar czf split-bill-backup-$(date +%Y%m%d).tar.gz /opt/split-bill
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Recovery Procedure

#### Scenario 1: MinIO Data Corruption

```bash
# Stop services
docker-compose -f docker/docker-compose.prod.yml down

# Restore from backup
tar xzf /backup/split-bill/20260211/minio.tar.gz -C /var/lib/docker/volumes/split-bill_minio_data/_data

# Restart
docker-compose -f docker/docker-compose.prod.yml up -d

# Verify
docker-compose -f docker/docker-compose.prod.yml exec minio ls /data
```

#### Scenario 2: Complete Server Failure

1. **Provision new server** with same specs
2. **Install Docker and Docker Compose**
3. **Restore configuration**:
   ```bash
   git clone <repository-url> /opt/split-bill
   scp .env.production root@new-server:/opt/split-bill/
   ```
4. **Restore data** from backup
5. **Start services**:
   ```bash
   cd /opt/split-bill
   docker-compose -f docker/docker-compose.prod.yml up -d
   ```
6. **Update DNS** to point to new server

#### Disaster Recovery Testing

Test recovery quarterly:
1. Create test environment
2. Restore from production backup
3. Verify all services work
4. Check data integrity
5. Document any issues

---

## Security

### Security Checklist

#### Infrastructure

- [ ] Firewall enabled (ufw/aws security groups)
- [ ] Only required ports open (80, 443)
- [ ] SSH key-based auth only (no passwords)
- [ ] Automatic security updates enabled
- [ ] Fail2ban installed and configured

#### Application

- [ ] Strong API keys (32+ random chars)
- [ ] HTTPS only (HSTS enabled)
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Security headers present
- [ ] No secrets in logs

#### Data

- [ ] MinIO access keys rotated regularly
- [ ] Redis password protected (if exposed)
- [ ] Backups encrypted
- [ ] Data retention policy documented

### Security Hardening

#### Server Hardening

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Install fail2ban
sudo apt-get install fail2ban
sudo systemctl enable fail2ban

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

#### Docker Security

```bash
# Run containers as non-root (update Dockerfiles)
USER appuser

# Limit container resources
docker run --memory=512m --cpus=1.0 split-bill-api

# Read-only root filesystem
docker run --read-only -v /tmp:/tmp split-bill-api
```

### Secret Management

#### Docker Secrets (Swarm Mode)

```bash
# Initialize swarm
docker swarm init

# Create secrets
echo "your-api-key" | docker secret create api_key -
echo "your-openrouter-key" | docker secret create openrouter_key -

# Use in compose
version: '3.8'
secrets:
  api_key:
    external: true

services:
  api:
    secrets:
      - api_key
```

#### AWS Secrets Manager

```python
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise e

# Usage
api_key = get_secret("split-bill/production/api-key")
```

---

## Performance Tuning

### Redis Optimization

```bash
# redis.conf optimizations
maxmemory 256mb
maxmemory-policy allkeys-lru
save ""  # Disable persistence if not needed (use only for cache)
```

### API Performance

#### Uvicorn Workers

```bash
# Production: workers = 2 * CPU cores + 1
uvicorn api.src.main:app --workers 4 --host 0.0.0.0 --port 8000
```

#### Connection Pooling

```python
# Redis connection pool
redis_client = redis.Redis(
    host='redis',
    port=6379,
    max_connections=50,
    socket_keepalive=True,
    socket_connect_timeout=5,
)
```

### Monitoring Performance

#### Key Metrics to Watch

| Metric | Target | Alert If |
|--------|--------|----------|
| Response Time (p95) | < 200ms | > 500ms |
| Error Rate | < 1% | > 5% |
| Cache Hit Rate | > 70% | < 50% |
| CPU Usage | < 70% | > 90% |
| Memory Usage | < 80% | > 95% |
| Disk Usage | < 80% | > 90% |

#### Load Testing

```bash
# Install hey (HTTP load generator)
go install github.com/rakyll/hey@latest

# Test health endpoint
hey -n 10000 -c 100 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.splitbill.yourdomain.com/health

# Test split calculation
hey -n 1000 -c 50 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -m POST \
  -d '{"person_names": ["A", "B"], "item_assignments": []}' \
  https://api.splitbill.yourdomain.com/splits/calculate
```

---

## Troubleshooting

### Common Production Issues

#### High Memory Usage

**Symptoms**: Container killed by OOM

**Diagnosis**:
```bash
# Check memory usage
docker stats

# Check for memory leaks in logs
docker-compose logs api | grep -i memory
```

**Solutions**:
1. Add memory limits to containers
2. Optimize Redis maxmemory
3. Check for memory leaks in application
4. Scale horizontally (add more instances)

#### Redis Connection Errors

**Symptoms**: API errors, slow responses

**Diagnosis**:
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Check connection count
docker-compose exec redis redis-cli info clients
```

**Solutions**:
1. Restart Redis: `docker-compose restart redis`
2. Increase connection pool size
3. Check network connectivity
4. Review Redis logs: `docker-compose logs redis`

#### MinIO Storage Full

**Symptoms**: Upload failures, errors in logs

**Diagnosis**:
```bash
# Check disk usage
df -h

# Check MinIO bucket size
docker-compose exec minio mc du local/split-bill
```

**Solutions**:
1. Clean old receipts: implement lifecycle policy
2. Increase disk size
3. Archive old data to cold storage
4. Set up alerts for disk usage

#### SSL Certificate Expired

**Symptoms**: HTTPS errors, browser warnings

**Fix**:
```bash
# Renew certificate
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal

# Restart nginx
sudo systemctl restart nginx
```

**Prevention**: Set up auto-renewal cron job

### Incident Response

#### Severity Levels

- **P1 (Critical)**: Service completely down
- **P2 (High)**: Major feature broken
- **P3 (Medium)**: Minor issue with workaround
- **P4 (Low)**: Cosmetic issue

#### Incident Response Runbook

**P1 Response**:
1. Acknowledge within 15 minutes
2. Assess impact (affected users, duration)
3. Attempt quick fix or rollback
4. Communicate status to stakeholders
5. Document incident timeline
6. Post-incident review within 24 hours

**Communication Template**:
```
[INCIDENT] Split Bill API - Degraded Performance

Status: Investigating
Impact: Slow response times (5-10s instead of <1s)
Start: 2026-02-11 10:00 UTC
ETA: Unknown

Updates:
10:15 UTC - Issue identified: Redis connection pool exhausted
10:30 UTC - Mitigation: Restarted Redis, scaling API instances
```

---

## Maintenance

### Regular Maintenance Tasks

#### Daily
- [ ] Check health endpoints
- [ ] Review error logs
- [ ] Monitor disk usage

#### Weekly
- [ ] Review metrics and performance
- [ ] Check for security updates
- [ ] Verify backup completion
- [ ] Review and rotate logs

#### Monthly
- [ ] Security audit
- [ ] Dependency updates
- [ ] SSL certificate check
- [ ] Performance review
- [ ] Disaster recovery test

#### Quarterly
- [ ] Full disaster recovery drill
- [ ] Security penetration test
- [ ] Architecture review
- [ ] Cost optimization review

### Updates and Patches

#### Security Updates

```bash
# Check for available updates
sudo apt-get update
sudo apt-get --just-print upgrade | grep "^Inst"

# Apply security updates only
sudo apt-get upgrade -y

# Restart services if needed
docker-compose -f docker/docker-compose.prod.yml restart
```

#### Application Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and deploy
docker-compose -f docker/docker-compose.prod.yml build
docker-compose -f docker/docker-compose.prod.yml up -d

# Verify deployment
curl -H "Authorization: Bearer KEY" https://api.yourdomain.com/health
```

#### Zero-Downtime Deployment

```bash
# Blue-green deployment
docker-compose -f docker-compose.prod.yml up -d --scale api=2

# Verify new instances
sleep 30
curl https://api.yourdomain.com/health

# Remove old instances
docker-compose -f docker-compose.prod.yml up -d --scale api=1
```

---

## Related Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [Development Guide](DEVELOPMENT.md)
- [API Reference](API.md)
- [TODO/Roadmap](TODO.md)

---

**Need Help?** Check logs, metrics, and health endpoints first. For urgent issues, refer to incident response procedures.
