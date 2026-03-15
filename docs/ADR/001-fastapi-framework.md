# ADR-001: FastAPI as Backend Framework

## Status

**Accepted** - Implemented and in production

## Context

We needed to choose a backend framework for the Split Bill API that would support:
- RESTful API development
- Async/await support for I/O operations (OCR, file storage)
- Automatic API documentation
- Type safety and validation
- Easy integration with AI services

## Decision

We chose **FastAPI** as our backend framework.

## Alternatives Considered

### 1. Flask

**Pros**:
- Mature ecosystem
- Flexible and lightweight
- Large community

**Cons**:
- No built-in async support (Flask 2.0+ has limited async)
- Requires additional libraries for validation (Marshmallow, Flask-RESTful)
- No automatic API documentation

**Verdict**: Rejected - Lacks native async support and automatic docs

### 2. Django + Django REST Framework

**Pros**:
- Full-featured framework
- Built-in admin interface
- ORM included

**Cons**:
- Overkill for our use case (no need for Django's ORM/admin)
- Steeper learning curve
- Slower development for simple APIs
- Not async-first

**Verdict**: Rejected - Too heavy for our simple API needs

### 3. FastAPI

**Pros**:
- Native async/await support
- Automatic OpenAPI/Swagger documentation
- Built on Pydantic for type validation
- High performance (on par with Node.js/Go)
- Dependency injection system
- Easy testing

**Cons**:
- Newer framework (smaller ecosystem than Flask/Django)
- Learning curve for advanced features

**Verdict**: **Accepted** - Best fit for our requirements

## Consequences

### Positive

1. **Rapid Development**: Automatic docs and type validation speed up development
2. **Type Safety**: Pydantic models catch errors at runtime
3. **Performance**: Async support means we can handle concurrent OCR requests efficiently
4. **Documentation**: Interactive Swagger UI at `/docs` for testing
5. **Standards**: Follows OpenAPI standards

### Negative

1. **Learning Curve**: Team needed to learn async patterns
2. **Ecosystem**: Fewer third-party extensions compared to Flask/Django
3. **Debugging**: Async stack traces can be harder to read

## Implementation

```python
# Example endpoint showing FastAPI features
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel

app = FastAPI()

class SplitRequest(BaseModel):
    person_names: list[str]
    tax_amount: float = 0.0

@app.post("/splits/calculate")
async def calculate_split(request: SplitRequest):
    # Automatic validation and documentation
    return {"result": "success"}
```

## Related Decisions

- ADR-002: Pydantic for Data Validation
- ADR-004: Uvicorn as ASGI Server

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI vs Flask Benchmarks](https://fastapi.tiangolo.com/benchmarks/)
- [Python Async Patterns](https://docs.python.org/3/library/asyncio.html)
