# ADR-006: API Key Authentication

## Status

**Accepted** - Implemented and in production

## Context

We need to secure the API endpoints to:
1. Prevent unauthorized access
2. Rate limit by client
3. Track usage
4. Protect against abuse

Requirements:
- Simple to implement
- Easy for clients to use
- Works with frontend (Streamlit) and API clients
- No user management overhead (initially)

## Decision

We chose **API Key Authentication** with Bearer tokens.

## Alternatives Considered

### 1. JWT (JSON Web Tokens)

**Pros**:
- Industry standard for user authentication
- Self-contained (contains claims)
- Can include expiration
- Stateless verification

**Cons**:
- Overkill for simple API access
- Token refresh complexity
- Requires user management system
- Larger tokens to transmit

**Verdict**: Rejected - Too complex for our current needs (no user accounts)

### 2. OAuth 2.0

**Pros**:
- Industry standard
- Third-party integration support
- Secure authorization flows

**Cons**:
- Complex implementation
- Requires OAuth provider
- Overhead for simple API
- Need to manage client IDs/secrets

**Verdict**: Rejected - Too complex for current scope

### 3. Basic Authentication

**Pros**:
- Simple to implement
- HTTP standard
- Widely supported

**Cons**:
- Credentials sent with every request
- Base64 encoding is not encryption
- Requires HTTPS (which we should have anyway)
- No token expiration

**Verdict**: Rejected - Less secure, credentials always transmitted

### 4. API Key with Bearer Token

**Pros**:
- Simple to implement
- Easy for clients (single header)
- Can rotate keys easily
- Works well with reverse proxies
- Standard pattern (similar to OpenAI, Stripe)
- Can add expiration later

**Cons**:
- Long-lived tokens (unless implemented)
- Key management needed
- No built-in user identity

**Verdict**: **Accepted** - Best balance for our use case

## Consequences

### Positive

1. **Simplicity**: Single environment variable for API key
2. **Easy Integration**: Works with curl, Postman, frontend
3. **Fast Verification**: Simple string comparison
4. **Flexible**: Can add user auth later without breaking changes
5. **Standard**: Familiar pattern for API consumers

### Negative

1. **Key Management**: Need to distribute and rotate keys
2. **No Identity**: Can't identify individual users (just clients)
3. **Long-lived**: Keys don't expire (unless manually rotated)
4. **Single Key**: All clients use same key (could use multiple keys)

## Implementation Details

### Header Format

```http
Authorization: Bearer YOUR_API_KEY
```

### FastAPI Implementation

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
API_KEY = os.environ.get("API_KEY", "default-dev-key")

async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Verify API key from Bearer token."""
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use Bearer.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials

# Usage in endpoints
@app.post("/splits/calculate")
async def calculate_split(api_key: str = Depends(get_api_key)):
    # API key verified, proceed with logic
    pass
```

### Client Usage Examples

#### cURL
```bash
curl -H "Authorization: Bearer my-secret-key" \
     http://localhost:8000/health
```

#### Python
```python
import requests

headers = {"Authorization": "Bearer my-secret-key"}
response = requests.post(
    "http://localhost:8000/splits/calculate",
    headers=headers,
    json={"person_names": ["Alice", "Bob"], ...}
)
```

#### JavaScript
```javascript
const response = await fetch('http://localhost:8000/health', {
    headers: {
        'Authorization': 'Bearer my-secret-key'
    }
});
```

### Key Generation

For development:
```bash
# Generate random API key
openssl rand -hex 32
# or
python -c "import secrets; print(secrets.token_hex(32))"
```

### Environment Configuration

```bash
# .env file
API_KEY=your-secure-random-key-here
```

### Security Considerations

1. **HTTPS Only**: Never use over HTTP in production
2. **Key Storage**:
   - Never commit to git
   - Use environment variables
   - Rotate periodically
3. **Header Exposure**: Don't log Authorization headers
4. **CORS**: Restrict origins in production

## Rate Limiting Integration

API key auth enables rate limiting per client:

```python
# Simple in-memory rate limiting (per IP)
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)

    def is_rate_limited(self, client_id: str, limit: int, window: int) -> bool:
        now = time.time()
        requests = self.requests[client_id]

        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in requests
            if now - req_time < window
        ]

        # Check limit
        if len(self.requests[client_id]) >= limit:
            return True

        self.requests[client_id].append(now)
        return False
```

## Future Evolution

### Phase 1: Single API Key (Current)
- One key for all clients
- Simple deployment
- Good for initial launch

### Phase 2: Multiple API Keys
- Different keys for different clients
- Per-key rate limits
- Usage tracking per client

### Phase 3: User Authentication (Future)
- JWT tokens for user sessions
- OAuth for third-party integrations
- API keys for service-to-service

## Migration Path

Adding user auth later won't break existing API key auth:

```python
# Future: Support both
async def get_current_user_or_key(
    api_key: Optional[str] = Depends(get_api_key_optional),
    token: Optional[str] = Depends(oauth2_scheme_optional)
):
    if token:
        return verify_jwt(token)
    if api_key:
        return verify_api_key(api_key)
    raise HTTPException(401, "Authentication required")
```

## Related Decisions

- ADR-001: FastAPI for backend (security integration)
- ADR-007: Docker for deployment (env var management)

## References

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Bearer Token RFC](https://tools.ietf.org/html/rfc6750)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)
