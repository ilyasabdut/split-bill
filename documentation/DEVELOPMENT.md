# Development Guide

## Overview

This guide covers everything you need to know to develop, test, and contribute to the Split Bill application.

**Version**: 2.0.0
**Last Updated**: February 2026

---

## Table of Contents

- [Quick Start](#quick-start)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Code Style](#code-style)
- [Testing](#testing)
- [Debugging](#debugging)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (optional but recommended)
- Git
- Make (for using Makefile commands)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd split-bill

# Install dependencies
make install

# Verify environment
make check_dotenv
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

**Required Environment Variables**:

```bash
# API Security
API_KEY=your-secure-random-key-here

# OCR Service
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODEL_NAME=mistralai/mistral-small-3.2-24b-instruct:free

# Storage (MinIO)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=split-bill
MINIO_USE_SSL=False

# Application URLs
APP_BASE_URL=http://localhost:8501
FASTAPI_API_URL=http://localhost:8000

# Optional
REDIS_URL=redis://localhost:6379
```

### 3. Run Development Servers

**Option A: Local Development (Two Terminals)**

Terminal 1 - Backend:
```bash
make run-api
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

Terminal 2 - Frontend:
```bash
make run-streamlit
# App available at http://localhost:8501
```

**Option B: Docker (Single Command)**

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up --build

# Access:
# Frontend: http://localhost:8501
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

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
- **Redis Insight**: Redis GUI (optional)

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

## Project Structure

```
split-bill/
├── api/                          # Backend (FastAPI)
│   ├── src/
│   │   ├── main.py              # Main application entry
│   │   ├── core/                # Core utilities
│   │   │   ├── cache.py        # Redis caching
│   │   │   ├── config.py       # Configuration
│   │   │   ├── logging.py      # Logging setup
│   │   │   ├── metrics.py      # Prometheus metrics
│   │   │   ├── monitoring.py   # Health checks
│   │   │   └── security.py     # Security utilities
│   │   ├── models/              # Data models
│   │   │   └── schemas.py      # Pydantic models
│   │   ├── routers/             # API routes
│   │   │   └── monitoring.py   # Health/metrics endpoints
│   │   ├── services/            # Business logic
│   │   │   ├── image_service.py
│   │   │   ├── minio_utils.py
│   │   │   ├── openrouter_ocr.py
│   │   │   └── split_logic.py
│   │   └── utils/               # Utilities
│   │       └── imports.py
│   └── tests/                   # Test suite
│       └── test_sample.py
│
├── app/                          # Frontend (Streamlit)
│   └── src/
│       ├── main.py              # Streamlit app entry
│       ├── state.py             # Session state management
│       ├── constants.py         # UI constants
│       ├── components/          # UI components
│       │   ├── steps/          # Wizard steps
│       │   │   ├── step_0_upload.py
│       │   │   ├── step_1_people.py
│       │   │   ├── step_2_assign_items.py
│       │   │   ├── step_3_tax_tip.py
│       │   │   └── step_4_results.py
│       │   └── ui.py           # Shared UI components
│       └── utils/               # Utilities
│           ├── api.py          # API client
│           └── ui.py           # UI helpers
│
├── docker/                       # Docker configurations
│   ├── Dockerfile               # Frontend Dockerfile
│   ├── Dockerfile.api           # Backend Dockerfile
│   ├── docker-compose.yml       # Development compose
│   ├── docker-compose.prod.yml  # Production compose
│   └── .dockerignore
│
├── documentation/                # Documentation
│   ├── README.md               # Overview
│   ├── ARCHITECTURE.md         # System architecture
│   ├── API.md                  # API documentation
│   ├── TODO.md                 # Roadmap and tasks
│   ├── DEVELOPMENT.md          # This file
│   ├── OPERATIONS.md           # Deployment guide
│   └── ADR/                    # Architecture decisions
│
├── scripts/                      # Utility scripts
│   └── demos/
│       └── phase1_demo.py
│
├── .env.example                  # Environment template
├── .gitignore
├── .pre-commit-config.yaml      # Pre-commit hooks
├── .streamlit/                  # Streamlit config
│   └── config.toml
├── AGENTS.md                    # AI coding guidelines
├── Makefile                     # Build automation
├── pyproject.toml              # Python dependencies
└── README.md                    # Main project readme
```

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
import redis

# Local imports
from core.config import settings
from services.ocr import extract_receipt_data
```

Use `isort` to automatically sort imports:
```bash
make sort-imports
```

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

### Test Structure

```
api/tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_main.py            # Main API tests
├── test_services/
│   ├── test_ocr.py
│   ├── test_split_logic.py
│   └── test_minio.py
└── test_routers/
    ├── test_receipts.py
    └── test_splits.py
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest api/tests/test_sample.py -v

# Run specific test
uv run pytest api/tests/test_sample.py::test_function -v

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
                "--port", "8000"
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
LOG_LEVEL=DEBUG make run-api
```

### Frontend Debugging

#### Streamlit Debugging

Enable debug mode:
```bash
streamlit run app/src/main.py --logger.level=debug
```

Print to Streamlit UI:
```python
import streamlit as st

# Display debug info
st.write("Debug:", variable)
st.json(data)
st.code(code_string)
```

#### API Client Debugging

```python
import requests
import logging

# Enable HTTP debugging
logging.basicConfig(level=logging.DEBUG)

# Or use requests hooks
def log_request(response, *args, **kwargs):
    print(f"Request: {response.request.method} {response.request.url}")
    print(f"Response: {response.status_code}")

response = requests.post(
    "http://localhost:8000/splits/calculate",
    json={...},
    hooks={'response': log_request}
)
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

### Adding a New API Endpoint

1. **Define model** in `api/src/models/schemas.py`:
```python
class NewRequest(BaseModel):
    field1: str
    field2: int

class NewResponse(BaseModel):
    result: str
```

2. **Add endpoint** in `api/src/main.py`:
```python
@app.post("/new-endpoint", response_model=NewResponse)
async def new_endpoint(request: NewRequest):
    return NewResponse(result="success")
```

3. **Add tests** in `api/tests/test_main.py`:
```python
def test_new_endpoint(client):
    response = client.post("/new-endpoint", json={"field1": "test", "field2": 42})
    assert response.status_code == 200
```

4. **Run quality checks**:
```bash
make check-all
```

### Adding a New Frontend Component

1. **Create component** in `app/src/components/`:
```python
import streamlit as st

def new_component():
    st.header("New Component")
    value = st.text_input("Enter value")
    return value
```

2. **Integrate** in `app/src/main.py`:
```python
from components.new_component import new_component

# In your main flow
value = new_component()
```

3. **Test manually**:
```bash
make run-streamlit
```

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

### Database Migrations (Future)

If we add a database layer:

```bash
# Create migration
alembic revision --autogenerate -m "add users table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'api'`

**Solution**: Ensure you're running from project root and Python path is set:
```bash
cd /path/to/split-bill
export PYTHONPATH="${PYTHONPATH}:$(pwd)/api/src"
make run-api
```

#### Port Already in Use

**Problem**: `Address already in use` when starting API

**Solution**: Kill existing process:
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use the Makefile (which handles this)
make run-api
```

#### Redis Connection Failed

**Problem**: `Connection refused` to Redis

**Solution**: Start Redis:
```bash
# With Docker
docker-compose -f docker/docker-compose.yml up redis

# Or locally
redis-server
```

#### Environment Variables Not Loading

**Problem**: `API_KEY` not found

**Solution**:
1. Check `.env` file exists
2. Verify `python-dotenv` is installed
3. Load explicitly:
```python
from dotenv import load_dotenv
load_dotenv()  # Add at start of main.py
```

#### Pre-commit Hooks Failing

**Problem**: Can't commit due to pre-commit errors

**Solution**:
```bash
# Run auto-fixes
make lint-fix
make format
make sort-imports

# Or skip hooks (not recommended for production code)
git commit --no-verify -m "message"
```

#### Type Checking Errors

**Problem**: MyPy errors

**Solution**:
```bash
# Run type check
make type-check

# Fix gradually - add type hints
# Use `Any` temporarily for complex cases (add TODO to fix)
from typing import Any

def function(data: Any) -> Any:
    # TODO: Add proper types
    pass
```

### Getting Help

1. **Check documentation**:
   - [Architecture](ARCHITECTURE.md)
   - [API Reference](API.md)
   - [TODO/Roadmap](TODO.md)

2. **Review error logs**:
   - Backend logs: Check terminal running `make run-api`
   - Frontend logs: Check terminal running `make run-streamlit`
   - Docker logs: `docker-compose logs`

3. **Test in isolation**:
   ```bash
   # Test just the backend
   make run-api
   curl http://localhost:8000/health

   # Test just the frontend
   make run-streamlit
   ```

4. **Create minimal reproduction**:
   - Strip down to simplest case that shows the issue
   - Share code snippet when asking for help

---

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
make check-all
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
- [ ] Type checking passes (`make type-check`)
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
