# System Architecture

## Overview

Split Bill is a production-ready receipt splitting application with OCR capabilities, built using a modern microservices-inspired architecture. The system separates concerns between a Streamlit frontend for user interaction and a FastAPI backend for business logic, with Redis for caching and MinIO for object storage.

**Version**: 2.0.0
**Last Updated**: February 2026

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                        │
│  │   Browser    │  │ Mobile App   │  │   API Client │                        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                        │
└─────────┼─────────────────┼─────────────────┼───────────────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROXY LAYER (Optional)                            │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    Nginx / Traefik                                  │    │
│  │         (SSL Termination, Load Balancing, Rate Limiting)            │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                 │
│                                                                             │
│  ┌─────────────────────────┐        ┌─────────────────────────┐            │
│  │   Streamlit Frontend    │◄──────►│    FastAPI Backend      │            │
│  │      (Port 8501)        │  HTTP  │      (Port 8000)        │            │
│  │                         │        │                         │            │
│  │  • UI Components        │        │  • REST API             │            │
│  │  • State Management     │        │  • Authentication       │            │
│  │  • API Client           │        │  • Business Logic       │            │
│  └─────────────────────────┘        └───────────┬─────────────┘            │
│                                                 │                          │
└─────────────────────────────────────────────────┼──────────────────────────┘
                                                  │
          ┌───────────────────────────────────────┼───────────────────┐
          │                                       │                   │
          ▼                                       ▼                   ▼
┌─────────────────────┐    ┌────────────────────────────┐    ┌──────────────────┐
│    Redis Cache      │    │      MinIO / S3            │    │   OpenRouter     │
│   (Port 6379)       │    │    Object Storage          │    │   AI Service     │
│                     │    │                            │    │                  │
│  • Split Results    │    │  • Receipt Images          │    │  • OCR Processing│
│  • OCR Results      │    │  • Metadata JSON           │    │  • Receipt Parsing│
│  • Session Data     │    │  • Share Links             │    │                  │
└─────────────────────┘    └────────────────────────────┘    └──────────────────┘
```

---

## Component Details

### 1. Frontend (Streamlit)

**Location**: `app/src/main.py`

**Responsibilities**:
- User interface rendering
- Form handling and validation
- Session state management
- API communication
- File upload handling

**Key Components**:
```
app/src/
├── main.py                    # Entry point
├── state.py                   # Session state management
├── constants.py               # UI constants
├── components/
│   ├── steps/                 # Step-by-step wizard
│   │   ├── step_0_upload.py   # Receipt upload
│   │   ├── step_1_people.py   # Add participants
│   │   ├── step_2_assign_items.py  # Item assignment
│   │   ├── step_3_tax_tip.py  # Tax/tip adjustment
│   │   └── step_4_results.py  # Results display
│   └── ui.py                  # Shared UI components
└── utils/
    ├── api.py                 # API client
    └── ui.py                  # UI utilities
```

**Design Pattern**: Step-by-step wizard with state persistence

### 2. Backend (FastAPI)

**Location**: `api/src/main.py`

**Responsibilities**:
- REST API endpoints
- Authentication and authorization
- Rate limiting
- Business logic orchestration
- External service integration

**Architecture Pattern**: Modular router-based structure

```
api/src/
├── main.py                    # Main application (integrated API)
├── core/                      # Core utilities
│   ├── config.py             # Configuration management
│   ├── security.py           # Security utilities
│   ├── cache.py              # Redis caching service
│   ├── logging.py            # Structured logging
│   ├── metrics.py            # Prometheus metrics
│   └── monitoring.py         # Health checks
├── models/
│   └── schemas.py            # Pydantic models
├── routers/                   # API route handlers
│   ├── monitoring.py         # Health/metrics endpoints
│   └── __init__.py
├── services/                  # Business logic
│   ├── openrouter_ocr.py     # OCR service
│   ├── split_logic.py        # Split calculation
│   ├── minio_utils.py        # Storage operations
│   └── image_service.py      # Image processing
└── utils/
    └── imports.py            # Import utilities
```

### 3. Cache Layer (Redis)

**Purpose**: High-performance caching for frequently accessed data

**Cache Strategies**:

| Data Type | TTL | Purpose |
|-----------|-----|---------|
| Split Results | 1 hour | Fast recalculation of same splits |
| OCR Results | 30 minutes | Avoid re-processing same receipts |
| Share Data | 24 hours | Quick access to shared splits |
| Health Check | 5 minutes | Cache connectivity verification |

**Implementation**: Located in `api/src/core/cache.py`

**Features**:
- Connection pooling (20 concurrent connections)
- Graceful fallback when Redis unavailable
- Async/await support
- Retry logic with exponential backoff

### 4. Storage Layer (MinIO/S3)

**Purpose**: Object storage for receipt images and metadata

**Data Structure**:
```
bucket: split-bill
├── receipts/
│   └── {split_id}.jpg        # Original/compressed receipt images
└── metadata/
    └── {split_id}.json       # Split calculation data
```

**Implementation**: Located in `api/src/services/minio_utils.py`

**Features**:
- Automatic bucket creation
- Presigned URLs for secure access
- Idempotent uploads (SHA256-based deduplication)

### 5. AI Service (OpenRouter)

**Purpose**: OCR and receipt data extraction

**Model**: Configurable (default: `mistralai/mistral-small-3.2-24b-instruct:free`)

**Process**:
1. Receive base64-encoded image
2. Send to OpenRouter API with structured prompt
3. Parse JSON response
4. Extract: items, prices, subtotal, tax, discounts

**Implementation**: Located in `api/src/services/openrouter_ocr.py`

---

## Data Flow Diagrams

### 1. Receipt Upload & OCR Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User    │────►│  Streamlit   │────►│   FastAPI    │────►│   Redis      │
│ Uploads  │     │   Frontend   │     │     API      │     │   (Check)    │
└──────────┘     └──────────────┘     └──────┬───────┘     └──────┬───────┘
                                             │                    │
                                             │ Cache Miss         │
                                             │                    │
                                             ▼                    │
                                      ┌──────────────┐           │
                                      │ Image Service│           │
                                      │• Compression │           │
                                      │• Validation  │           │
                                      └──────┬───────┘           │
                                             │                    │
                                             ▼                    │
                                      ┌──────────────┐            │
                                      │  OpenRouter  │            │
                                      │     OCR      │            │
                                      └──────┬───────┘            │
                                             │                     │
                                             ▼                     │
                                      ┌──────────────┐             │
                                      │   Response   │─────────────┘
                                      │   + Cache    │
                                      └──────────────┘
```

### 2. Split Calculation Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User    │────►│  Streamlit   │────►│   FastAPI    │────►│   Redis      │
│ Submits  │     │   Frontend   │     │     API      │     │   (Check)    │
│  Split   │     │              │     │              │     │              │
└──────────┘     └──────────────┘     └──────┬───────┘     └──────┬───────┘
                                             │                    │
                                             │ Cache Miss         │
                                             │                    │
                                             ▼                    │
                                      ┌──────────────┐           │
                                      │ Split Logic  │           │
                                      │• Calculate   │           │
                                      │• Distribute  │           │
                                      │  Tax/Tip     │           │
                                      └──────┬───────┘           │
                                             │                    │
                                             ▼                    │
                                      ┌──────────────┐           │
                                      │   Generate   │           │
                                      │   Share Link │           │
                                      └──────┬───────┘           │
                                             │                    │
                                             ▼                    │
                                      ┌──────────────┐           │
                                      │   Response   │────────────┘
                                      │   + Cache    │
                                      └──────────────┘
```

### 3. View Shared Split Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User    │────►│   Browser    │────►│   FastAPI    │────►│   Redis      │
│ Opens    │     │   (Direct)   │     │     API      │     │   (Check)    │
│  Link    │     │              │     │ /splits/view │     │              │
└──────────┘     └──────────────┘     └──────┬───────┘     └──────┬───────┘
                                             │                    │
                                             │ Cache Miss         │
                                             │                    │
                                             ▼                    │
                                      ┌──────────────┐           │
                                      │    MinIO     │           │
                                      │   Get JSON   │           │
                                      └──────┬───────┘           │
                                             │                    │
                                             ▼                    │
                                      ┌──────────────┐           │
                                      │   Response   │────────────┘
                                      │   + Cache    │
                                      └──────────────┘
```

---

## Security Architecture

### Authentication

**Method**: API Key (Bearer Token)

```
┌─────────────────────────────────────────────────────────────┐
│                    Authentication Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Client Request          │  Authorization: Bearer <api_key> │
│           │              │                                  │
│           ▼              │                                  │
│  ┌──────────────────┐    │                                  │
│  │  FastAPI Security│    │  Validates:                      │
│  │  (HTTPBearer)    │────┤  • Scheme = "Bearer"            │
│  └──────────────────┘    │  • credentials == API_KEY       │
│           │              │                                  │
│           ▼              │                                  │
│  ┌──────────────────┐    │  If Invalid:                     │
│  │  Protected Route │    │  • 401 Unauthorized             │
│  └──────────────────┘    │  • WWW-Authenticate header      │
│                          │                                  │
└─────────────────────────────────────────────────────────────┘
```

### Rate Limiting

**Implementation**: Simple sliding window algorithm in memory

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/receipts/upload` | 10 requests | 1 minute |
| `/splits/calculate` | 30 requests | 1 minute |
| `/splits/view/{id}` | 100 requests | 1 minute |

**Behavior**:
1. Track requests per client IP
2. Clean expired requests outside window
3. Reject if limit exceeded (429 Too Many Requests)

### Security Headers

All responses include:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'
```

### Input Validation

**Request Size Limit**: 10MB maximum
**File Validation**:
- Content-Type: image/jpeg, image/png, image/jpg
- Size: < 2MB (frontend), < 10MB (backend)
- Format: Valid image headers

### CORS Policy

```python
allow_origins=["*"]  # Development
# Production: Restrict to specific origins
```

---

## Caching Strategy

### Cache Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Cache Architecture                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│   │   Client    │───►│   FastAPI   │───►│    Redis    │              │
│   └─────────────┘    └──────┬──────┘    └──────┬──────┘              │
│                             │                  │                     │
│                        Cache Key Generation    │                     │
│                        • SHA256 hash          │                     │
│                        • Deterministic        │                     │
│                        • Idempotent          │                     │
│                                                                       │
│   Cache Strategies:                                                   │
│   ├─ Split Results: TTL 1 hour (frequent recalculation)              │
│   ├─ OCR Results: TTL 30 minutes (expensive operation)               │
│   ├─ Share Data: TTL 24 hours (persistent sharing)                   │
│   └─ Health Check: TTL 5 minutes (monitoring)                        │
│                                                                       │
│   Fallback: If Redis unavailable, direct processing                  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Cache Key Generation

**Split Calculation**:
```python
idempotency_key_material = {
    "people": sorted(person_names),
    "assignments": sorted([...], key=lambda x: x["item"]),
    "tax": tax_amount,
    "tip": tip_amount,
    "split_evenly": split_evenly,
}
key = SHA256(json.dumps(idempotency_key_material, sort_keys=True)).hexdigest()[:12]
```

**Benefits**:
- Same inputs = Same cache key
- Order-independent (sorted)
- Deterministic across requests

---

## Data Models

### Core Models

**CalculateSplitRequest**:
```python
{
    "person_names": List[str],
    "item_assignments": List[{
        "item_details": {"item": str, "price": float},
        "assigned_to": List[str]
    }],
    "tax_amount_input": float = 0.0,
    "tip_amount_input": float = 0.0,
    "split_evenly": bool = False,
    "extracted_subtotal_from_gemini": Optional[float] = None,
    "extracted_total_discount": float = 0.0
}
```

**CalculateSplitResponse**:
```python
{
    "split_results": Dict[str, {
        "subtotal": float,
        "tax": float,
        "tip": float,
        "total": float,
        "items": List[{ "item": str, "price": float }]
    }],
    "share_link": str,
    "split_id": str
}
```

**OCR Response**:
```python
{
    "items": List[{ "item": str, "price": float }],
    "subtotal": float,
    "tax": float,
    "total": float,
    "discounts": List[{ "description": str, "amount": float }]
}
```

---

## Error Handling Strategy

### Error Hierarchy

```
Exception
├── HTTPException (FastAPI)
│   ├── 400 Bad Request (Invalid input)
│   ├── 401 Unauthorized (Invalid API key)
│   ├── 413 Payload Too Large (File size)
│   ├── 429 Too Many Requests (Rate limit)
│   └── 500 Internal Server Error (Unexpected)
└── Service Exceptions
    ├── OCRProcessingError
    ├── CacheConnectionError
    └── StorageError
```

### Error Response Format

```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 400,
        "detail": "Invalid request format"
    }
}
```

### Global Exception Handlers

Located in `api/src/main.py`:
- HTTPException handler (preserves status codes)
- Generic Exception handler (returns 500, logs details)

---

## Monitoring & Observability

### Health Checks

**Endpoint**: `GET /health`

```json
{
    "status": "healthy",
    "timestamp": 1735689600.0,
    "version": "2.0.0",
    "security": "enabled",
    "caching": "enabled",
    "monitoring": {
        "uptime_seconds": 3600,
        "requests_total": 150,
        "errors_total": 2,
        "splits_calculated": 50
    },
    "cache": "connected"
}
```

### Metrics

**Endpoint**: `GET /metrics`

Collected metrics:
- Request count (total, by endpoint)
- Error rate
- Cache hit/miss ratio
- OCR processing time
- Split calculation count
- Uptime

### Logging

**Structured Logging** with correlation IDs:
```python
{
    "timestamp": "2026-02-11T10:30:00Z",
    "level": "INFO",
    "logger": "main",
    "message": "Processing split calculation",
    "request_id": "uuid",
    "user_agent": "...",
    "endpoint": "/splits/calculate"
}
```

---

## Scalability Considerations

### Current Architecture Limits

| Component | Limit | Notes |
|-----------|-------|-------|
| Rate Limiting | Per-instance | Memory-based, not distributed |
| Cache | Single Redis | No clustering |
| Storage | Single MinIO | No multi-region |
| OCR | OpenRouter API | External dependency |

### Horizontal Scaling Path

1. **Rate Limiting**: Replace with Redis-based distributed rate limiting
2. **Cache**: Redis Cluster or Valkey
3. **Storage**: Multi-region MinIO or cloud S3
4. **API**: Stateless, can run multiple instances behind load balancer
5. **Frontend**: Streamlit can run multiple instances

### Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API Response (cached) | < 200ms | P95 |
| API Response (OCR) | < 2s | P95 |
| Cache Hit Rate | 70-90% | Based on usage patterns |
| Error Rate | < 5% | Includes OCR failures |
| Uptime | 99.9% | Includes maintenance windows |

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Streamlit | 1.45.0 | UI Framework |
| Backend | FastAPI | 0.115.12 | API Framework |
| Server | Uvicorn | 0.34.3 | ASGI Server |
| Cache | Redis | 7.x | Caching |
| Storage | MinIO | Latest | Object Storage |
| OCR | OpenRouter | API v1 | AI Service |
| Language | Python | 3.12+ | Runtime |
| Container | Docker | 24.x | Containerization |
| Orchestration | Docker Compose | 2.x | Local Dev |

---

## Related Documentation

- [API Documentation](API.md) - Detailed API reference
- [Development Guide](DEVELOPMENT.md) - Setup and contribution
- [Operations Guide](OPERATIONS.md) - Deployment and monitoring
- [TODO/Roadmap](TODO.md) - Active development items
- [Architecture Decisions](ADR/) - Design decision records
