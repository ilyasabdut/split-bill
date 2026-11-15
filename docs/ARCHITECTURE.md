# System Architecture

## Overview

Split Bill is a receipt splitting application with OCR. Three containers: a SvelteKit static PWA (`web/`), a FastAPI backend (`api/`) and Postgres. See [PROJECT_AUDIT.md](PROJECT_AUDIT.md) for what is and is not implemented.

---

## Component Details

### Backend (FastAPI)

**Location**: `api/src/main.py`

**Responsibilities**:
- REST API endpoints
- Authentication and authorization
- Rate limiting
- Business logic orchestration
- External service integration

**Layout**: `api/src/main.py` (app, splits, receipts), `api/src/routers/` (currency, groups, templates, payments, analytics), `api/src/services/` (OCR, image, currency), `api/src/db/` (SQLAlchemy models; migrations in `api/alembic/`).

### AI Service (OpenRouter)

**Purpose**: OCR and receipt data extraction

**Model**: Configurable (default: `mistralai/mistral-small-3.2-24b-instruct:free`)

**Process**:
1. Receive base64-encoded image
2. Send to OpenRouter API with structured prompt
3. Parse JSON response
4. Extract: items, prices, subtotal, tax, discounts

**Implementation**: Located in `api/src/services/openrouter_ocr.py`

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
└── HTTPException (FastAPI)
    ├── 400 Bad Request (Invalid input)
    ├── 401 Unauthorized (Invalid API key)
    ├── 413 Payload Too Large (File size)
    ├── 429 Too Many Requests (Rate limit)
    └── 500 Internal Server Error (Unexpected)
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

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | SvelteKit (static PWA) | 2.x | UI Framework |
| Backend | FastAPI | 0.115.12 | API Framework |
| Server | Uvicorn | 0.34.3 | ASGI Server |
| Database | PostgreSQL | 16 | Groups, templates, payments |
| OCR | OpenRouter | API v1 | AI Service |
| Language | Python | 3.12+ | Runtime |
| Container | Docker | 24.x | Containerization |
| Orchestration | Docker Compose | 2.x | Local Dev |

---

## Related Documentation

- [API Documentation](API.md) - Detailed API reference
- [Development Guide](DEVELOPMENT.md) - Setup and contribution
- [Operations Guide](OPERATIONS.md) - Deployment
- [TODO/Roadmap](TODO.md) - Active development items
- [Architecture Decisions](ADR/) - Design decision records
