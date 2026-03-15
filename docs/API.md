# API Documentation

## Overview

The Split Bill API provides RESTful endpoints for receipt OCR processing and bill splitting calculations. All endpoints require authentication via API key.

**Base URL**: `http://localhost:8000` (development)
**Version**: 2.0.0
**Last Updated**: February 2026

---

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Request/Response Examples](#requestresponse-examples)

---

## Authentication

All API endpoints require authentication using an API key passed as a Bearer token in the Authorization header.

### Header Format

```http
Authorization: Bearer YOUR_API_KEY
```

### Example

```bash
curl -H "Authorization: Bearer my-secret-api-key" \
     http://localhost:8000/health
```

### Security Notes

- API keys should be kept secret and never exposed in client-side code
- Use environment variables to store API keys
- Rotate keys periodically for security
- Use HTTPS in production to protect keys in transit

### Authentication Errors

**401 Unauthorized** - Invalid or missing API key
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 401,
        "detail": "Invalid or missing API Key"
    }
}
```

---

## Endpoints

### Health Check

Check API health status and view system metrics.

**Endpoint**: `GET /health`

**Rate Limit**: None

**Headers**:
```http
Authorization: Bearer YOUR_API_KEY
```

#### Success Response (200)

```json
{
    "status": "healthy",
    "timestamp": 1735689600.0,
    "version": "2.0.0",
    "security": "enabled",
    "caching": "enabled",
    "monitoring": {
        "uptime_seconds": 3600.5,
        "requests_total": 150,
        "errors_total": 2,
        "splits_calculated": 50
    },
    "cache": "connected"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| status | string | "healthy" or "unhealthy" |
| timestamp | float | Unix timestamp |
| version | string | API version |
| security | string | Security status |
| caching | string | Caching status |
| monitoring.uptime_seconds | float | Server uptime |
| monitoring.requests_total | int | Total requests handled |
| monitoring.errors_total | int | Total errors |
| monitoring.splits_calculated | int | Total splits calculated |
| cache | string | Cache connection status |

#### Error Response (401)

```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 401,
        "detail": "Invalid or missing API Key"
    }
}
```

---

### Get Metrics

Retrieve detailed application metrics.

**Endpoint**: `GET /metrics`

**Rate Limit**: None

**Headers**:
```http
Authorization: Bearer YOUR_API_KEY
```

#### Success Response (200)

```json
{
    "application": {
        "version": "2.0.0",
        "uptime_seconds": 3600.5,
        "status": "running"
    },
    "requests": {
        "total": 150,
        "errors": 2,
        "error_rate": 0.013
    },
    "business": {
        "splits_calculated": 50
    },
    "cache": {
        "hits": 85,
        "misses": 15,
        "hit_rate": 0.85
    },
    "timestamp": 1735689600.0
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| application.version | string | API version |
| application.uptime_seconds | float | Server uptime |
| application.status | string | Application status |
| requests.total | int | Total requests |
| requests.errors | int | Total errors |
| requests.error_rate | float | Error rate (0-1) |
| business.splits_calculated | int | Total splits calculated |
| cache.hits | int | Cache hits |
| cache.misses | int | Cache misses |
| cache.hit_rate | float | Cache hit rate (0-1) |

---

### Upload Receipt

Upload a receipt image for OCR processing.

**Endpoint**: `POST /receipts/upload`

**Rate Limit**: 10 requests per minute

**Headers**:
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: multipart/form-data
```

#### Request Body

**Content-Type**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | Receipt image (JPG, PNG, max 2MB) |

#### cURL Example

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@receipt.jpg" \
  http://localhost:8000/receipts/upload
```

#### Python Example

```python
import requests

url = "http://localhost:8000/receipts/upload"
headers = {"Authorization": "Bearer YOUR_API_KEY"}

with open("receipt.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, headers=headers, files=files)

print(response.json())
```

#### Success Response (200)

```json
{
    "parsed_data": {
        "items": [
            {"item": "Burger", "price": 12.99},
            {"item": "Fries", "price": 4.50},
            {"item": "Soda", "price": 2.99}
        ],
        "subtotal": 20.48,
        "tax": 1.84,
        "total": 22.32,
        "discounts": [
            {"description": "10% Off", "amount": 2.05}
        ]
    },
    "processed_image_bytes_base64": "/9j/4AAQSkZJRgABAQEASABIAAD...",
    "extracted_subtotal_from_gemini": 20.48,
    "extracted_total_discount": 2.05
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| parsed_data.items | array | List of items with name and price |
| parsed_data.items[].item | string | Item name |
| parsed_data.items[].price | number | Item price |
| parsed_data.subtotal | number | Subtotal amount |
| parsed_data.tax | number | Tax amount |
| parsed_data.total | number | Total amount |
| parsed_data.discounts | array | List of discounts |
| parsed_data.discounts[].description | string | Discount description |
| parsed_data.discounts[].amount | number | Discount amount |
| processed_image_bytes_base64 | string | Base64 encoded compressed image |
| extracted_subtotal_from_gemini | number | Extracted subtotal |
| extracted_total_discount | number | Total discount amount |

#### Error Responses

**400 Bad Request** - Invalid file or OCR error
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 400,
        "detail": "Error: Failed to parse receipt"
    }
}
```

**413 Payload Too Large** - File too large
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 413,
        "detail": "Request too large. Maximum size is 10MB."
    }
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 429,
        "detail": "Rate limit exceeded. Maximum 10 requests per minute."
    }
}
```

**500 Internal Server Error** - Processing error
```json
{
    "error": {
        "type": "InternalServerError",
        "status_code": 500,
        "detail": "An unexpected error occurred"
    }
}
```

---

### Calculate Split

Calculate bill split among multiple people with item assignments.

**Endpoint**: `POST /splits/calculate`

**Rate Limit**: 30 requests per minute

**Headers**:
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

#### Request Body

```json
{
    "person_names": ["Alice", "Bob", "Charlie"],
    "item_assignments": [
        {
            "item_details": {
                "item": "Burger",
                "price": 12.99
            },
            "assigned_to": ["Alice"]
        },
        {
            "item_details": {
                "item": "Fries",
                "price": 4.50
            },
            "assigned_to": ["Bob", "Charlie"]
        },
        {
            "item_details": {
                "item": "Soda",
                "price": 2.99
            },
            "assigned_to": ["Alice", "Bob", "Charlie"]
        }
    ],
    "tax_amount_input": 1.84,
    "tip_amount_input": 4.00,
    "split_evenly": false,
    "extracted_subtotal_from_gemini": 20.48,
    "extracted_total_discount": 0.0
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| person_names | array[string] | Yes | List of participant names |
| item_assignments | array | Yes | Item assignments with details |
| item_assignments[].item_details | object | Yes | Item information |
| item_assignments[].item_details.item | string | Yes | Item name |
| item_assignments[].item_details.price | number | Yes | Item price |
| item_assignments[].assigned_to | array[string] | Yes | People assigned to this item |
| tax_amount_input | number | No | Tax amount (default: 0) |
| tip_amount_input | number | No | Tip amount (default: 0) |
| split_evenly | boolean | No | Split entire bill evenly (default: false) |
| extracted_subtotal_from_gemini | number | No | OCR subtotal for even split calculation |
| extracted_total_discount | number | No | Total discount amount (default: 0) |

#### cURL Example

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "person_names": ["Alice", "Bob"],
    "item_assignments": [
        {
            "item_details": {"item": "Pizza", "price": 20.00},
            "assigned_to": ["Alice", "Bob"]
        }
    ],
    "tax_amount_input": 1.80,
    "tip_amount_input": 4.00
  }' \
  http://localhost:8000/splits/calculate
```

#### Python Example

```python
import requests

url = "http://localhost:8000/splits/calculate"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
payload = {
    "person_names": ["Alice", "Bob"],
    "item_assignments": [
        {
            "item_details": {"item": "Pizza", "price": 20.00},
            "assigned_to": ["Alice", "Bob"]
        }
    ],
    "tax_amount_input": 1.80,
    "tip_amount_input": 4.00
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

#### Success Response (200)

```json
{
    "split_results": {
        "Alice": {
            "subtotal": 11.49,
            "tax": 0.92,
            "tip": 2.00,
            "total": 14.41,
            "items": [
                {"item": "Burger", "price": 12.99},
                {"item": "Soda", "price": 1.00}
            ]
        },
        "Bob": {
            "subtotal": 5.24,
            "tax": 0.46,
            "tip": 1.00,
            "total": 6.70,
            "items": [
                {"item": "Fries", "price": 2.25},
                {"item": "Soda", "price": 1.00}
            ]
        },
        "Charlie": {
            "subtotal": 5.24,
            "tax": 0.46,
            "tip": 1.00,
            "total": 6.70,
            "items": [
                {"item": "Fries", "price": 2.25},
                {"item": "Soda", "price": 1.00}
            ]
        }
    },
    "share_link": "http://localhost:8501/splits/view/a1b2c3d4e5f6",
    "split_id": "a1b2c3d4e5f6"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| split_results | object | Split calculation per person |
| split_results.{name}.subtotal | number | Person's subtotal |
| split_results.{name}.tax | number | Person's tax share |
| split_results.{name}.tip | number | Person's tip share |
| split_results.{name}.total | number | Person's total |
| split_results.{name}.items | array | Items assigned to person |
| share_link | string | Shareable link to view results |
| split_id | string | Unique split identifier |

#### Even Split Example

When `split_evenly: true`, the subtotal is divided equally:

```json
{
    "person_names": ["Alice", "Bob", "Charlie"],
    "item_assignments": [],
    "tax_amount_input": 3.00,
    "tip_amount_input": 5.00,
    "split_evenly": true,
    "extracted_subtotal_from_gemini": 50.00
}
```

Response:
```json
{
    "split_results": {
        "Alice": {
            "subtotal": 16.67,
            "tax": 1.00,
            "tip": 1.67,
            "total": 19.34,
            "items": []
        },
        "Bob": {
            "subtotal": 16.67,
            "tax": 1.00,
            "tip": 1.67,
            "total": 19.34,
            "items": []
        },
        "Charlie": {
            "subtotal": 16.66,
            "tax": 1.00,
            "tip": 1.66,
            "total": 19.32,
            "items": []
        }
    },
    "share_link": "http://localhost:8501/splits/view/a1b2c3d4e5f6",
    "split_id": "a1b2c3d4e5f6"
}
```

#### Error Responses

**400 Bad Request** - Invalid request format
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 400,
        "detail": "Invalid request: person_names must be a non-empty list"
    }
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 429,
        "detail": "Rate limit exceeded. Maximum 30 requests per minute."
    }
}
```

**500 Internal Server Error** - Calculation error
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 500,
        "detail": "Calculation error: Division by zero"
    }
}
```

---

### View Split

Retrieve shared split data by ID.

**Endpoint**: `GET /splits/view/{split_id}`

**Rate Limit**: 100 requests per minute

**Headers**:
```http
Authorization: Bearer YOUR_API_KEY
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| split_id | string | Yes | Unique split identifier |

#### cURL Example

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/splits/view/a1b2c3d4e5f6
```

#### Python Example

```python
import requests

url = "http://localhost:8000/splits/view/a1b2c3d4e5f6"
headers = {"Authorization": "Bearer YOUR_API_KEY"}

response = requests.get(url, headers=headers)
print(response.json())
```

#### Success Response (200)

```json
{
    "split_id": "a1b2c3d4e5f6",
    "original_parsed_data": {
        "items": [
            {"item": "Burger", "price": 12.99},
            {"item": "Fries", "price": 4.50}
        ],
        "subtotal": 17.49,
        "tax": 1.57,
        "total": 19.06
    },
    "person_names": ["Alice", "Bob"],
    "item_assignments": [
        {
            "item_details": {"item": "Burger", "price": 12.99},
            "assigned_to": ["Alice"]
        },
        {
            "item_details": {"item": "Fries", "price": 4.50},
            "assigned_to": ["Bob"]
        }
    ],
    "split_evenly_choice": false,
    "total_discount_applied": 0.0,
    "user_adjusted_tax": 1.57,
    "user_adjusted_tip": 3.00,
    "calculated_split_results": {
        "Alice": {
            "subtotal": 12.99,
            "tax": 1.10,
            "tip": 2.10,
            "total": 16.19
        },
        "Bob": {
            "subtotal": 4.50,
            "tax": 0.47,
            "tip": 0.90,
            "total": 5.87
        }
    },
    "creation_timestamp": 1735689600.0
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| split_id | string | Unique split identifier |
| original_parsed_data | object | Original OCR data |
| person_names | array[string] | List of participants |
| item_assignments | array | Item assignment details |
| split_evenly_choice | boolean | Whether even split was used |
| total_discount_applied | number | Total discount amount |
| user_adjusted_tax | number | Tax amount used |
| user_adjusted_tip | number | Tip amount used |
| calculated_split_results | object | Split calculation per person |
| creation_timestamp | float | Unix timestamp of creation |

#### Error Responses

**404 Not Found** - Split ID not found
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 404,
        "detail": "Split not found"
    }
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 429,
        "detail": "Rate limit exceeded. Maximum 100 requests per minute."
    }
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse and ensure fair usage.

### Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /receipts/upload` | 10 requests | 1 minute |
| `POST /splits/calculate` | 30 requests | 1 minute |
| `GET /splits/view/{id}` | 100 requests | 1 minute |
| Other endpoints | No limit | - |

### Rate Limit Response

When rate limit is exceeded, the API returns:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45
```

```json
{
    "error": {
        "type": "HTTPException",
        "status_code": 429,
        "detail": "Rate limit exceeded. Maximum {limit} requests per minute."
    }
}
```

### Best Practices

1. **Implement client-side rate limiting** - Track your request rate
2. **Handle 429 responses gracefully** - Implement exponential backoff
3. **Cache results** - Avoid recalculating identical splits
4. **Batch operations** - Group related requests when possible

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
    "error": {
        "type": string,      // Error type/classification
        "status_code": int,  // HTTP status code
        "detail": string     // Human-readable message
    }
}
```

### HTTP Status Codes

| Code | Meaning | When Returned |
|------|---------|---------------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input, malformed JSON, OCR error |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Split ID doesn't exist |
| 413 | Payload Too Large | Request body > 10MB or file > 2MB |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

### Error Types

- **HTTPException**: Standard HTTP errors (400, 401, 404, 429)
- **InternalServerError**: Unexpected server errors (500)
- **ValidationError**: Request validation errors (400)

### Handling Errors

#### Python Example

```python
import requests

url = "http://localhost:8000/splits/calculate"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
payload = {"person_names": ["Alice"], "item_assignments": []}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    print(f"Split calculated: {data['split_id']}")
elif response.status_code == 429:
    print("Rate limit exceeded. Please wait...")
elif response.status_code == 401:
    print("Invalid API key. Check your credentials.")
else:
    error = response.json()
    print(f"Error {error['error']['status_code']}: {error['error']['detail']}")
```

#### JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/splits/calculate', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        person_names: ['Alice'],
        item_assignments: []
    })
});

if (response.ok) {
    const data = await response.json();
    console.log(`Split calculated: ${data.split_id}`);
} else if (response.status === 429) {
    console.log('Rate limit exceeded. Please wait...');
} else {
    const error = await response.json();
    console.error(`Error ${error.error.status_code}: ${error.error.detail}`);
}
```

---

## Request/Response Examples

### Complete Workflow Example

#### 1. Health Check

```bash
curl -H "Authorization: Bearer secret123" \
     http://localhost:8000/health
```

#### 2. Upload Receipt

```bash
curl -X POST \
  -H "Authorization: Bearer secret123" \
  -F "file=@dinner_receipt.jpg" \
  http://localhost:8000/receipts/upload
```

Response:
```json
{
    "parsed_data": {
        "items": [
            {"item": "Steak", "price": 25.99},
            {"item": "Wine", "price": 12.00},
            {"item": "Salad", "price": 8.99}
        ],
        "subtotal": 46.98,
        "tax": 4.23,
        "total": 51.21,
        "discounts": []
    },
    "processed_image_bytes_base64": "/9j/4AAQ...",
    "extracted_subtotal_from_gemini": 46.98,
    "extracted_total_discount": 0.0
}
```

#### 3. Calculate Split

```bash
curl -X POST \
  -H "Authorization: Bearer secret123" \
  -H "Content-Type: application/json" \
  -d '{
    "person_names": ["John", "Jane"],
    "item_assignments": [
        {
            "item_details": {"item": "Steak", "price": 25.99},
            "assigned_to": ["John"]
        },
        {
            "item_details": {"item": "Wine", "price": 12.00},
            "assigned_to": ["John", "Jane"]
        },
        {
            "item_details": {"item": "Salad", "price": 8.99},
            "assigned_to": ["Jane"]
        }
    ],
    "tax_amount_input": 4.23,
    "tip_amount_input": 8.00
  }' \
  http://localhost:8000/splits/calculate
```

Response:
```json
{
    "split_results": {
        "John": {
            "subtotal": 31.99,
            "tax": 2.88,
            "tip": 5.44,
            "total": 40.31,
            "items": [
                {"item": "Steak", "price": 25.99},
                {"item": "Wine", "price": 6.00}
            ]
        },
        "Jane": {
            "subtotal": 14.99,
            "tax": 1.35,
            "tip": 2.56,
            "total": 18.90,
            "items": [
                {"item": "Wine", "price": 6.00},
                {"item": "Salad", "price": 8.99}
            ]
        }
    },
    "share_link": "http://localhost:8501/splits/view/abc123def456",
    "split_id": "abc123def456"
}
```

#### 4. View Split

```bash
curl -H "Authorization: Bearer secret123" \
     http://localhost:8000/splits/view/abc123def456
```

---

## OpenAPI Specification

The API provides an interactive Swagger UI for testing:

**URL**: `http://localhost:8000/docs`

The OpenAPI schema is available at:

**URL**: `http://localhost:8000/openapi.json`

---

## SDK and Client Libraries

### Python

```python
import requests
from typing import List, Dict, Any

class SplitBillAPI:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def upload_receipt(self, file_path: str) -> Dict[str, Any]:
        """Upload receipt for OCR processing."""
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{self.base_url}/receipts/upload",
                headers=self.headers,
                files=files
            )
        response.raise_for_status()
        return response.json()

    def calculate_split(
        self,
        person_names: List[str],
        item_assignments: List[Dict],
        tax: float = 0,
        tip: float = 0
    ) -> Dict[str, Any]:
        """Calculate bill split."""
        payload = {
            "person_names": person_names,
            "item_assignments": item_assignments,
            "tax_amount_input": tax,
            "tip_amount_input": tip
        }
        response = requests.post(
            f"{self.base_url}/splits/calculate",
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        return response.json()

# Usage
api = SplitBillAPI("http://localhost:8000", "your-api-key")
result = api.calculate_split(
    person_names=["Alice", "Bob"],
    item_assignments=[...],
    tax=2.50,
    tip=5.00
)
```

---

## Related Documentation

- [Architecture Overview](ARCHITECTURE.md) - System architecture and data flow
- [Development Guide](DEVELOPMENT.md) - Development setup and guidelines
- [Operations Guide](OPERATIONS.md) - Deployment and monitoring
