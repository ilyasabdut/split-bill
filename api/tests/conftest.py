"""
Test configuration and fixtures for split-bill API unit tests.
This is a simplified version for unit tests that don't require async database.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock


# Mock fixtures for unit tests

@pytest.fixture
def mock_cache_service():
    """Mock cache service."""
    return MagicMock()

@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    redis = AsyncMock()
    redis.ping = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.setex = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.exists = AsyncMock(return_value=1)
    redis.keys = AsyncMock(return_value=[])
    redis.ttl = AsyncMock(return_value=3600)
    redis.info = AsyncMock(return_value={
        "connected_clients": 5,
        "used_memory_human": "10MB",
        "used_memory_peak_human": "15MB",
        "total_commands_processed": 1000,
        "keyspace_hits": 800,
        "keyspace_misses": 200,
    })
    return redis

@pytest.fixture
def mock_api_key():
    """Mock API key."""
    return "test-api-key"

@pytest.fixture
def mock_secret_key():
    """Mock secret key."""
    return "test-secret-key"

@pytest.fixture
def mock_settings():
    """Mock settings."""
    return MagicMock(
        API_KEY="test-api-key",
        SECRET_KEY="test-secret-key",
        LOG_LEVEL="INFO",
        LOG_FORMAT="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        REDIS_URL="redis://localhost:6379",
        OPENROUTER_API_KEY="test-openrouter-key",
        OPENROUTER_MODEL_NAME="test-model",
        OPENROUTER_API_BASE_URL="https://openrouter.ai/api/v1",
        MINIO_ENDPOINT="localhost:9000",
        MINIO_ACCESS_KEY="minio-access-key",
        MINIO_SECRET_KEY="minio-secret-key",
        MINIO_BUCKET_NAME="test-bucket",
        MINIO_USE_SSL=False,
        DATABASE_URL="sqlite:///:memory:",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        RATE_LIMIT_PER_MINUTE=60,
        MAX_IMAGE_SIZE_MB=2,
    )
