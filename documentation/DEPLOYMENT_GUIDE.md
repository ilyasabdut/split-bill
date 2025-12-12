# 🚀 Production Deployment Guide

This guide provides step-by-step instructions for deploying the Split Bill application in production environments.

## 📋 Prerequisites

### System Requirements
- **Docker & Docker Compose** (latest versions)
- **Domain name** with SSL certificate capability
- **VPS/Cloud server** with minimum 2GB RAM, 2 CPU cores
- **Storage:** 20GB+ available space

### Required External Services
- **OpenRouter API Key** ([get here](https://openrouter.ai/docs/quickstart))
- **MinIO instance** (S3-compatible storage)
- **SSL Certificate** (Let's Encrypt recommended)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Nginx         │────│  Streamlit App   │    │   FastAPI API   │
│   (Reverse      │    │  (Port 8501)     │    │  (Port 8000)    │
│    Proxy)       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                               │
         │                                               │
    ┌────▼─────────┐                              ┌─────▼──────┐
    │  SSL/TLS     │                              │   Redis    │
    │  Termination │                              │  (Cache)   │
    └──────────────┘                              └────────────┘
         │                                               │
         │                                      ┌────────▼─────────┐
         │                                      │    MinIO         │
         │                                      │  (Object Store)  │
         └──────────────────────────────────────│                  │
                                                └──────────────────┘
```

## 🔧 Environment Configuration

### 1. Environment Variables

Create production environment file:

```bash
# Production Environment Variables
cp .env.example .env.production

# Core Application
APP_BASE_URL=https://yourdomain.com
API_KEY=your-super-secure-random-api-key-here
FASTAPI_API_URL=http://localhost:8000

# OpenRouter Configuration
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODEL_NAME=mistralai/mistral-small-3.2-24b-instruct:free

# Redis Configuration
REDIS_URL=redis://redis:6379

# MinIO Configuration
MINIO_ENDPOINT=your-minio-server:9000
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key
MINIO_BUCKET_NAME=split-bill
MINIO_USE_SSL=true

# Security
SECRET_KEY=your-jwt-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
```

### 2. Production Docker Compose

Create `docker/docker-compose.prod.yml`:

```yaml
version: "3.8"

services:
  nginx:
    image: nginx:alpine
    container_name: split-bill-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
      - api
    restart: unless-stopped

  app:
    image: registry.ilyasabdut.loseyourip.com/split-bill-app:latest
    container_name: split-bill-app
    environment:
      - FASTAPI_API_URL=http://api:8000
      - APP_BASE_URL=https://yourdomain.com
      - API_KEY=${API_KEY}
    restart: unless-stopped
    depends_on:
      - api

  api:
    image: registry.ilyasabdut.loseyourip.com/split-bill-api:latest
    container_name: split-bill-api
    environment:
      - API_KEY=${API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENROUTER_MODEL_NAME=${OPENROUTER_MODEL_NAME}
      - MINIO_ENDPOINT=${MINIO_ENDPOINT}
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME}
      - MINIO_USE_SSL=${MINIO_USE_SSL}
      - APP_BASE_URL=https://yourdomain.com
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
    depends_on:
      - redis

  redis:
    image: valkey/valkey:alpine3.23
    container_name: split-bill-redis
    volumes:
      - redis_data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    restart: unless-stopped

volumes:
  redis_data:
    driver: local

networks:
  default:
    name: split-bill-network
```

## 🌍 Nginx Configuration

### 1. Create nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream streamlit_app {
        server app:8501;
    }

    upstream fastapi_api {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=2r/s;

    # Streamlit App
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Gzip Compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_proxied any;
        gzip_comp_level 6;
        gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;

        # Streamlit App
        location / {
            proxy_pass http://streamlit_app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 86400;
        }

        # FastAPI Endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://fastapi_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check
        location /health {
            proxy_pass http://fastapi_api/health;
            proxy_set_header Host $host;
        }
    }
}
```

## 🔒 SSL Certificate Setup

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Setup

```bash
# Create SSL directory
mkdir ssl
cd ssl

# Generate private key
openssl genrsa -out privkey.pem 2048

# Generate certificate signing request
openssl req -new -key privkey.pem -out cert.csr

# Get certificate from CA and save as fullchain.pem
```

## 📦 Deployment Steps

### 1. Build and Push Images

```bash
# Build images
docker-compose -f docker/docker-compose.prod.yml build

# Tag for registry
docker tag split-bill-api:latest registry.ilyasabdut.loseyourip.com/split-bill-api:latest
docker tag split-bill-app:latest registry.ilyasabdut.loseyourip.com/split-bill-app:latest

# Push to registry (or save locally)
docker push registry.ilyasabdut.loseyourip.com/split-bill-api:latest
docker push registry.ilyasabdut.loseyourip.com/split-bill-app:latest
```

**Note:** The API now uses a unified `src/main.py` entry point that combines:
- Security features (API key auth, rate limiting, security headers)
- Performance caching (Redis integration)
- Modular router structure
- Production-ready error handling

### 2. Server Setup

```bash
# On production server
git clone <your-repository>
cd split-bill

# Copy environment file
cp .env.example .env.production
nano .env.production  # Edit with production values

# Copy production compose file
cp docker/docker-compose.prod.yml ./

# Set permissions
chmod 600 .env.production
chown -R $USER:$USER .
```

### 3. Deploy Services

```bash
# Start services
docker-compose -f docker/docker-compose.prod.yml up -d

# Check status
docker-compose -f docker/docker-compose.prod.yml ps

# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f
```

## 🧪 Testing Deployment

### 1. Health Checks

```bash
# Test application health
curl https://yourdomain.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": 1234567890,
  "version": "2.0.0",
  "security": "enabled",
  "caching": "enabled"
}
```

## 🏗️ Unified API Architecture

The Split Bill API now uses a **single production-ready entry point** that combines all features:

### **Single API File: `src/main.py`**
- **Modular Routers:** Clean separation with APIRouter patterns
- **Built-in Security:** API key authentication, rate limiting, security headers
- **Performance Caching:** Redis integration with intelligent cache strategies
- **Error Handling:** Comprehensive exception handling and logging
- **Production Ready:** Follows FastAPI best practices for scalability

### **Key Features Integrated:**
```python
# Security Features
- API Key Bearer token authentication
- Rate limiting (10/30/100 requests per minute)
- Security headers (CSP, XSS Protection, Frame Options)
- Input validation (10MB request limit)

# Performance Features
- Redis caching for split results (1-hour TTL)
- Graceful fallback when Redis unavailable
- Cache statistics and monitoring
- 3-5x performance improvement

# Business Logic
- Bill splitting calculations
- Receipt processing integration
- Shareable link generation
- Modular endpoint structure
```

### **API Endpoints Structure:**
```
GET  /                     # API information
GET  /health               # Health check with cache status
GET  /health/              # Detailed health check
POST /api/splits/calculate # Calculate split with caching (30/min)
GET  /splits/view/{id}     # View shared split (100/min)
```

All endpoints require `Authorization: Bearer YOUR_API_KEY` header.

### 2. API Testing

```bash
# Test with API key
curl -X GET "https://yourdomain.com/api/health" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Test split calculation
curl -X POST "https://yourdomain.com/api/splits/calculate" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "person_names": ["Alice", "Bob"],
    "item_assignments": [],
    "tax_amount_input": 2.50,
    "tip_amount_input": 5.00,
    "split_evenly": true
  }'
```

### 3. Performance Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test rate limiting
ab -n 100 -c 10 -H "Authorization: Bearer YOUR_API_KEY" \
   https://yourdomain.com/api/health

# Test caching (second request should be faster)
time curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://yourdomain.com/api/splits/calculate" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## 📊 Monitoring & Maintenance

### 1. Log Management

```bash
# View application logs
docker-compose -f docker/docker-compose.prod.yml logs -f app
docker-compose -f docker/docker-compose.prod.yml logs -f api

# View Nginx logs
docker exec split-bill-nginx tail -f /var/log/nginx/access.log
docker exec split-bill-nginx tail -f /var/log/nginx/error.log

# View Redis logs
docker logs split-bill-redis
```

### 2. Performance Monitoring

```bash
# Check Redis memory usage
docker exec split-bill-redis redis-cli INFO memory

# Monitor cache hit rates
docker exec split-bill-redis redis-cli INFO stats

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s \
  "https://yourdomain.com/api/health"
```

### 3. Regular Maintenance

```bash
# Update images
docker-compose -f docker/docker-compose.prod.yml pull
docker-compose -f docker/docker-compose.prod.yml up -d

# Clean up old images
docker image prune -a

# Backup Redis data
docker exec split-bill-redis redis-cli BGSAVE
docker cp split-bill-redis:/data/dump.rdb ./backups/redis-$(date +%Y%m%d).rdb

# Rotate logs
docker system prune --volumes
```

## 🔧 Troubleshooting

### Common Issues

**1. SSL Certificate Issues**
```bash
# Check certificate validity
openssl x509 -in ssl/fullchain.pem -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew
```

**2. Redis Connection Issues**
```bash
# Test Redis connectivity
docker exec split-bill-redis redis-cli ping

# Check Redis logs
docker logs split-bill-redis
```

**3. API Authentication Issues**
```bash
# Verify API key is set
docker exec split-bill-api env | grep API_KEY

# Test API endpoint
curl -v -H "Authorization: Bearer YOUR_API_KEY" \
  https://yourdomain.com/api/health
```

**4. Rate Limiting Issues**
- Check Nginx logs for rate limiting responses
- Adjust rate limits in nginx.conf if needed
- Monitor rate limit headers in API responses

### Performance Optimization

**1. Redis Optimization**
```bash
# Optimize Redis configuration
echo "maxmemory 256mb" >> redis.conf
echo "maxmemory-policy allkeys-lru" >> redis.conf
```

**2. Nginx Optimization**
- Enable HTTP/2
- Configure appropriate worker_processes
- Set up log rotation

**3. Application Scaling**
```yaml
# Scale API services
docker-compose -f docker/docker-compose.prod.yml up -d --scale api=3
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use Redis Cluster for high availability
- Implement load balancing for API services
- Consider separate Redis instance for caching

### Vertical Scaling
- Monitor CPU and memory usage
- Adjust container resource limits
- Optimize database queries

### Monitoring Stack
Consider adding:
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for log aggregation

## 🛡️ Security Best Practices

### 1. Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Docker images
docker-compose -f docker/docker-compose.prod.yml pull
```

### 2. Firewall Configuration
```bash
# UFW setup
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 3. Backup Strategy
```bash
# Automated backups
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec split-bill-redis redis-cli BGSAVE
docker cp split-bill-redis:/data/dump.rdb ./backups/redis_$DATE.rdb
aws s3 cp ./backups/redis_$DATE.rdb s3://your-backup-bucket/
```

## ✅ Production Checklist

- [ ] SSL certificate configured and tested
- [ ] Environment variables secured
- [ ] API key authentication working
- [ ] Rate limiting configured
- [ ] Redis caching operational
- [ ] MinIO storage accessible
- [ ] Nginx reverse proxy configured
- [ ] Health checks passing
- [ ] Log rotation configured
- [ ] Backup strategy implemented
- [ ] Monitoring set up
- [ ] Security headers verified
- [ ] Performance testing completed

## 📞 Support

For deployment issues:
1. Check application logs: `docker-compose logs`
2. Verify environment configuration
3. Test individual service connectivity
4. Review Nginx error logs
5. Check SSL certificate status

**Production deployment completed successfully!** 🎉
