# Development Guide

## Overview

This guide covers everything you need to know to develop, test, and contribute to the Split Bill application.

**Version**: 2.0.0
**Last Updated**: February 2026

---

## Table of Contents

- [Quick Start](#quick-start)
- [Development Environment](#development-environment)
- [Code Style](#code-style)
- [Testing](#testing)
- [Debugging](#debugging)
- [Common Tasks](#common-tasks)

---

## Quick Start

Prerequisites: Python 3.12+ with [uv](https://docs.astral.sh/uv/), [Bun](https://bun.sh), Docker, Make.

```bash
cp .env.example .env   # then fill in API_KEY and OPENROUTER_API_KEY
make install           # uv sync + bun install

# Option A: everything in Docker (web :15173, api :18000, postgres :15432)
make up

# Option B: local dev servers against Dockerised postgres
make infra-up
cd api && uv run alembic upgrade head   # uses sqlalchemy.url from api/alembic.ini
make start
```

The api container applies alembic migrations on start (`alembic upgrade head`).

---

## Development Environment

### Recommended Tools

#### Required
- **Python 3.12+**: Core runtime
- **uv**: Fast Python package manager (comes with `make install`)
- **Git**: Version control

#### Optional but Recommended
- **VS Code**: IDE with Python extension
- **Docker Desktop**: For containerized development
- **Postman**: API testing

### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".venv": true
    }
}
```

Recommended extensions:
- Python (Microsoft)
- Ruff
- Black Formatter
- Docker
- Markdown All in One

---

## Code Style

### Python Style Guide

We follow PEP 8 with these modifications:

#### Line Length
- **88 characters** (Black default)
- Use parentheses for implicit line continuation

```python
# Good
result = some_function(
    arg1=value1,
    arg2=value2,
    arg3=value3
)

# Bad
result = some_function(arg1=value1, arg2=value2, arg3=value3)  # Too long
```

#### Imports

Order: stdlib → third-party → local

```python
# Standard library
import os
import sys
from typing import Dict, List, Optional

# Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local imports
from services.openrouter_ocr import extract_receipt_data
```

`make format` (ruff) fixes import order.

#### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Variables | snake_case | `user_name` |
| Functions | snake_case | `calculate_split()` |
| Classes | PascalCase | `SplitCalculator` |
| Constants | UPPER_CASE | `MAX_FILE_SIZE` |
| Private | _leading_underscore | `_internal_helper()` |

#### Type Hints

Use type hints for all function parameters and return types:

```python
from typing import Dict, List, Optional

def calculate_split(
    item_assignments: List[Dict[str, Any]],
    person_names: List[str],
    tax_amount: float = 0.0,
) -> Dict[str, Dict[str, float]]:
    """Calculate split amounts per person."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def process_receipt(image_bytes: bytes) -> Dict[str, Any]:
    """Process a receipt image and extract data.

    Args:
        image_bytes: Raw image data in bytes.

    Returns:
        Dictionary containing extracted receipt data with keys:
        - items: List of items with name and price
        - subtotal: Subtotal amount
        - tax: Tax amount
        - total: Total amount

    Raises:
        ValueError: If image is invalid or cannot be processed.
        HTTPException: If OCR service fails.

    Example:
        >>> result = process_receipt(image_data)
        >>> print(result['total'])
        32.50
    """
    pass
```

### FastAPI Patterns

#### Dependency Injection

```python
from fastapi import Depends

async def get_cache_service():
    return cache_service

@app.post("/splits/calculate")
async def calculate_split(
    cache: CacheService = Depends(get_cache_service)
):
    # Use cache
    pass
```

#### Exception Handling

```python
from fastapi import HTTPException

@app.post("/receipts/upload")
async def upload_receipt(file: UploadFile):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    # Process file
```

#### Response Models

Always use Pydantic models for responses:

```python
from pydantic import BaseModel

class SplitResponse(BaseModel):
    split_id: str
    share_link: str
    results: Dict[str, Any]

@app.post("/splits/calculate", response_model=SplitResponse)
async def calculate_split(request: SplitRequest):
    return SplitResponse(...)
```

---

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest api/tests/test_splits.py -v

# Run specific test
uv run pytest api/tests/test_splits.py::test_function -v

# Run with coverage
uv run pytest --cov=api/src --cov-report=html

# Run with debugging
uv run pytest -v --pdb
```

### Writing Tests

#### Unit Test Example

```python
import pytest
from services.split_logic import calculate_split

def test_calculate_split_even():
    """Test even split calculation."""
    # Arrange
    person_names = ["Alice", "Bob"]
    tax = 2.00
    tip = 4.00

    # Act
    result = calculate_split(
        item_assignments=[],
        tax_str=str(tax),
        tip_str=str(tip),
        person_names=person_names,
        split_evenly_flag=True,
        overall_subtotal_for_even_split=20.00
    )

    # Assert
    assert "Alice" in result
    assert "Bob" in result
    assert result["Alice"]["subtotal"] == 10.00
    assert result["Alice"]["tax"] == 1.00
    assert result["Alice"]["tip"] == 2.00
    assert result["Alice"]["total"] == 13.00
```

#### Integration Test Example

```python
import pytest
from fastapi.testclient import TestClient
from api.src.main import app

client = TestClient(app)

def test_upload_receipt():
    """Test receipt upload endpoint."""
    # Prepare test file
    with open("tests/fixtures/receipt.jpg", "rb") as f:
        response = client.post(
            "/receipts/upload",
            headers={"Authorization": "Bearer test-key"},
            files={"file": ("receipt.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    assert "parsed_data" in response.json()
```

#### Async Test Example

```python
import pytest
from services.cache import cache_service

@pytest.mark.asyncio
async def test_cache_service():
    """Test cache operations."""
    await cache_service.connect()

    # Set value
    await cache_service.set("test_key", {"data": "value"})

    # Get value
    result = await cache_service.get("test_key")
    assert result == {"data": "value"}

    await cache_service.disconnect()
```

### Fixtures

Create reusable test fixtures in `conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from api.src.main import app

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Authenticated headers fixture."""
    return {"Authorization": "Bearer test-api-key"}

@pytest.fixture
async def cache():
    """Cache service fixture."""
    from core.cache import cache_service
    await cache_service.connect()
    yield cache_service
    await cache_service.disconnect()
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

def test_ocr_with_mock():
    """Test OCR with mocked OpenRouter."""
    mock_response = {
        "items": [{"item": "Burger", "price": 10.00}],
        "total": 10.00
    }

    with patch('services.openrouter_ocr.extract_receipt_data') as mock_ocr:
        mock_ocr.return_value = mock_response

        result = process_receipt(b"fake_image_data")

        assert result["total"] == 10.00
        mock_ocr.assert_called_once()
```

---

## Debugging

### Backend Debugging

#### Using pdb (Python Debugger)

```python
import pdb

def calculate_split(...):
    # Set breakpoint
    pdb.set_trace()

    # Your code here
    result = process_items(items)

    return result
```

Common pdb commands:
- `n` - Next line
- `s` - Step into function
- `c` - Continue execution
- `p variable` - Print variable
- `l` - List code around current line
- `q` - Quit debugger

#### Using VS Code Debugger

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "api.src.main:app",
                "--reload",
                "--port", "18000"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

#### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

# Different log levels
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.exception("Error with traceback")  # Includes exception info
```

Enable debug logging:
```bash
LOG_LEVEL=DEBUG make start
```

### Docker Debugging

#### View Container Logs

```bash
# All services
docker-compose -f docker/docker-compose.yml logs -f

# Specific service
docker-compose -f docker/docker-compose.yml logs -f api
```

#### Enter Running Container

```bash
# Bash shell in API container
docker-compose -f docker/docker-compose.yml exec api bash

# Python shell
docker-compose -f docker/docker-compose.yml exec api python
```

#### Debug Container Startup

```bash
# Run with explicit command to debug
docker-compose -f docker/docker-compose.yml run --rm api bash

# Check environment variables
docker-compose -f docker/docker-compose.yml exec api env
```

---

## Common Tasks

### Adding Dependencies

1. **Edit** `pyproject.toml`:
```toml
[project]
dependencies = [
    "existing-package>=1.0.0",
    "new-package>=2.0.0",  # Add here
]
```

2. **Install**:
```bash
make install
```

3. **Commit** both `pyproject.toml` and updated `uv.lock`

## Contributing

### Workflow

1. **Create feature branch**:
```bash
git checkout -b feature/my-feature
```

2. **Make changes**:
   - Write code
   - Add tests
   - Update documentation

3. **Run quality checks**:
```bash
make check
```

4. **Commit**:
```bash
git add .
git commit -m "feat: add new feature"
```

5. **Push and create PR**:
```bash
git push origin feature/my-feature
```

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add receipt history endpoint

fix(ocr): handle null image bytes

docs: update API documentation with examples
```

### Code Review Checklist

Before submitting PR:

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] All tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation updated
- [ ] Environment variables documented
- [ ] No hardcoded secrets
- [ ] Error handling implemented

---

## Related Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [API Reference](API.md)
- [Operations Guide](OPERATIONS.md)
- [TODO/Roadmap](TODO.md)
- [Architecture Decisions](ADR/)

---

**Questions?** Check the [troubleshooting section](#troubleshooting) or open an issue.
