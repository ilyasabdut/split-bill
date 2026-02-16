"""
Unit tests for core.cache module.
Tests Redis cache service functionality.
"""

import json
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest

from src.core.cache import CacheService, REDIS_URL


@pytest.fixture
def cache_service():
    """Create a fresh CacheService instance for each test."""
    return CacheService()


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
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


class TestCacheServiceInitialization:
    """Test CacheService initialization."""

    def test_redis_url_from_env(self, monkeypatch):
        """Test that REDIS_URL is loaded from environment."""
        monkeypatch.setenv("REDIS_URL", "redis://custom:6379")
        from src.core.cache import REDIS_URL
        assert REDIS_URL == "redis://custom:6379"

    def test_default_redis_url(self):
        """Test default REDIS_URL value."""
        assert REDIS_URL == "redis://localhost:6379"

    def test_cache_service_init(self):
        """Test CacheService initialization."""
        service = CacheService()
        assert service.redis_url == REDIS_URL
        assert service._redis is None
        assert service._connection_pool is None


class TestCacheServiceConnection:
    """Test Redis connection management."""

    @pytest.mark.asyncio
    async def test_connect_success(self, cache_service, mock_redis):
        """Test successful Redis connection."""
        with patch("src.core.cache.aioredis.from_url", return_value=mock_redis):
            await cache_service.connect()
            assert cache_service._redis is not None
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_ping_failure(self, cache_service, mock_redis):
        """Test connection failure when ping fails."""
        mock_redis.ping = AsyncMock(return_value=False)
        with patch("src.core.cache.aioredis.from_url", return_value=mock_redis):
            with pytest.raises(RuntimeError, match="Redis ping failed"):
                await cache_service.connect()
            assert cache_service._redis is None

    @pytest.mark.asyncio
    async def test_connect_exception(self, cache_service):
        """Test connection failure due to exception."""
        with patch("src.core.cache.aioredis.from_url", side_effect=Exception("Connection error")):
            with pytest.raises(Exception, match="Connection error"):
                await cache_service.connect()
            assert cache_service._redis is None

    @pytest.mark.asyncio
    async def test_disconnect(self, cache_service, mock_redis):
        """Test disconnection from Redis."""
        cache_service._redis = mock_redis
        await cache_service.disconnect()
        mock_redis.close.assert_called_once()
        assert cache_service._redis is None

    @pytest.mark.asyncio
    async def test_disconnect_no_connection(self, cache_service):
        """Test disconnect when no connection exists."""
        await cache_service.disconnect()
        assert cache_service._redis is None

    @pytest.mark.asyncio
    async def test_get_redis_creates_connection(self, cache_service, mock_redis):
        """Test get_redis creates connection if needed."""
        with patch("src.core.cache.aioredis.from_url", return_value=mock_redis):
            redis = await cache_service.get_redis()
            assert redis is not None
            assert cache_service._redis is not None

    @pytest.mark.asyncio
    async def test_get_redis_returns_existing(self, cache_service, mock_redis):
        """Test get_redis returns existing connection."""
        cache_service._redis = mock_redis
        redis = await cache_service.get_redis()
        assert redis == mock_redis


class TestCacheServiceGet:
    """Test cache get operations."""

    @pytest.mark.asyncio
    async def test_get_success(self, cache_service, mock_redis):
        """Test successful cache get."""
        test_data = {"key": "value"}
        mock_redis.get = AsyncMock(return_value=json.dumps(test_data))
        cache_service._redis = mock_redis

        result = await cache_service.get("test_key")
        assert result == test_data
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_not_found(self, cache_service, mock_redis):
        """Test cache get when key not found."""
        mock_redis.get = AsyncMock(return_value=None)
        cache_service._redis = mock_redis

        result = await cache_service.get("nonexistent_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_no_connection(self, cache_service):
        """Test cache get when no connection exists."""
        result = await cache_service.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_exception(self, cache_service, mock_redis):
        """Test cache get with exception."""
        mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))
        cache_service._redis = mock_redis

        result = await cache_service.get("test_key")
        assert result is None


class TestCacheServiceSet:
    """Test cache set operations."""

    @pytest.mark.asyncio
    async def test_set_success(self, cache_service, mock_redis):
        """Test successful cache set."""
        cache_service._redis = mock_redis
        result = await cache_service.set("test_key", {"data": "value"})
        assert result is True
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_timedelta_expiry(self, cache_service, mock_redis):
        """Test cache set with timedelta expiry."""
        cache_service._redis = mock_redis
        expire = timedelta(hours=1)
        result = await cache_service.set("test_key", {"data": "value"}, expire=expire)
        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_seconds_expiry(self, cache_service, mock_redis):
        """Test cache set with seconds expiry."""
        cache_service._redis = mock_redis
        result = await cache_service.set("test_key", {"data": "value"}, expire_seconds=3600)
        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_no_connection(self, cache_service):
        """Test cache set when no connection exists."""
        result = await cache_service.set("test_key", {"data": "value"})
        assert result is False

    @pytest.mark.asyncio
    async def test_set_exception(self, cache_service, mock_redis):
        """Test cache set with exception."""
        mock_redis.set = AsyncMock(side_effect=Exception("Redis error"))
        cache_service._redis = mock_redis

        result = await cache_service.set("test_key", {"data": "value"})
        assert result is False


class TestCacheServiceDelete:
    """Test cache delete operations."""

    @pytest.mark.asyncio
    async def test_delete_success(self, cache_service, mock_redis):
        """Test successful cache delete."""
        cache_service._redis = mock_redis
        result = await cache_service.delete("test_key")
        result is True
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_no_connection(self, cache_service):
        """Test cache delete when no connection exists."""
        result = await cache_service.delete("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_exception(self, cache_service, mock_redis):
        """Test cache delete with exception."""
        mock_redis.delete = AsyncMock(side_effect=Exception("Redis error"))
        cache_service._redis = mock_redis

        result = await cache_service.delete("test_key")
        assert result is False


class TestCacheServiceExists:
    """Test cache exists operations."""

    @pytest.mark.asyncio
    async def test_exists_true(self, cache_service, mock_redis):
        """Test cache exists when key exists."""
        mock_redis.exists = AsyncMock(return_value=1)
        cache_service._redis = mock_redis

        result = await cache_service.exists("test_key")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, cache_service, mock_redis):
        """Test cache exists when key doesn't exist."""
        mock_redis.exists = AsyncMock(return_value=0)
        cache_service._redis = mock_redis

        result = await cache_service.exists("test_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_no_connection(self, cache_service):
        """Test cache exists when no connection exists."""
        result = await cache_service.exists("test_key")
        assert result is False


class TestCacheServiceClearPattern:
    """Test cache clear pattern operations."""

    @pytest.mark.asyncio
    async def test_clear_pattern_success(self, cache_service, mock_redis):
        """Test successful clear pattern."""
        mock_redis.keys = AsyncMock(return_value=["key1", "key2"])
        mock_redis.delete = AsyncMock(return_value=2)
        cache_service._redis = mock_redis

        result = await cache_service.clear_pattern("cache:split:*")
        assert result == 2
        mock_redis.keys.assert_called_once_with("cache:split:*")

    @pytest.mark.asyncio
    async def test_clear_pattern_no_keys(self, cache_service, mock_redis):
        """Test clear pattern when no keys match."""
        mock_redis.keys = AsyncMock(return_value=[])
        cache_service._redis = mock_redis

        result = await cache_service.clear_pattern("cache:split:*")
        assert result == 0


class TestCacheServiceGetTTL:
    """Test cache TTL operations."""

    @pytest.mark.asyncio
    async def test_get_ttl(self, cache_service, mock_redis):
        """Test get TTL for a key."""
        mock_redis.ttl = AsyncMock(return_value=3600)
        cache_service._redis = mock_redis

        result = await cache_service.get_ttl("test_key")
        assert result == 3600

    @pytest.mark.asyncio
    async def test_get_ttl_no_connection(self, cache_service):
        """Test get TTL when no connection exists."""
        result = await cache_service.get_ttl("test_key")
        assert result == -2


class TestCacheServiceKeyGenerators:
    """Test cache key generation methods."""

    def test_split_result_key(self, cache_service):
        """Test split result key generation."""
        key = cache_service.split_result_key("split-123")
        assert key == "cache:split:result:split-123"

    def test_ocr_result_key(self, cache_service):
        """Test OCR result key generation."""
        key = cache_service.ocr_result_key("hash-abc")
        assert key == "cache:ocr:result:hash-abc"

    def test_share_data_key(self, cache_service):
        """Test share data key generation."""
        key = cache_service.share_data_key("split-456")
        assert key == "cache:share:data:split-456"

    def test_user_session_key(self, cache_service):
        """Test user session key generation."""
        key = cache_service.user_session_key("session-789")
        assert key == "cache:session:session-789"


class TestCacheServiceSplitMethods:
    """Test split-specific cache methods."""

    @pytest.mark.asyncio
    async def test_get_split_result(self, cache_service, mock_redis):
        """Test get split result."""
        test_data = {"split_id": "123", "result": "data"}
        mock_redis.get = AsyncMock(return_value=json.dumps(test_data))
        cache_service._redis = mock_redis

        result = await cache_service.get_split_result("split-123")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_set_split_result(self, cache_service, mock_redis):
        """Test set split result."""
        cache_service._redisredis = mock_redis
        result = await cache_service.set_split_result("split-123", {"result": "data"})
        assert result is True

    @pytest.mark.asyncio
    async def test_invalidate_split_result(self, cache_service, mock_redis):
        """Test invalidate split result."""
        cache_service._redis = mock_redis
        result = await cache_service.invalidate_split_result("split-123")
        assert result is True


class TestCacheServiceOCRMethods:
    """Test OCR-specific cache methods."""

    @pytest.mark.asyncio
    async def test_get_ocr_result(self, cache_service, mock_redis):
        """Test get OCR result."""
        test_data = {"image_hash": "abc", "result": "data"}
        mock_redis.get = AsyncMock(return_value=json.dumps(test_data))
        cache_service._redis = mock_redis

        result = await cache_service.get_ocr_result("hash-abc")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_set_ocr_result(self, cache_service, mock_redis):
        """Test set OCR result."""
        cache_service._redis = mock_redis
        result = await cache_service.set_ocr_result("hash-abc", {"result": "data"})
        assert result is True

    @pytest.mark.asyncio
    async def test_invalidate_ocr_result(self, cache_service, mock_redis):
        """Test invalidate OCR result."""
        cache_service._redis = mock_redis
        result = await cache_service.invalidate_ocr_result("hash-abc")
        assert result is True


class TestCacheServiceShareMethods:
    """Test share-specific cache methods."""

    @pytest.mark.asyncio
    async def test_get_share_data(self, cache_service, mock_redis):
        """Test get share data."""
        test_data = {"split_id": "123", "share": "data"}
        mock_redis.get = AsyncMock(return_value=json.dumps(test_data))
        cache_service._redis = mock_redis

        result = await cache_service.get_share_data("split-123")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_set_share_data(self, cache_service, mock_redis):
        """Test set share data."""
        cache_service._redis = mock_redis
        result = await cache_service.set_share_data("split-123", {"share": "data"})
        assert result is True

    @pytest.mark.asyncio
    async def test_invalidate_share_data(self, cache_service, mock_redis):
        """Test invalidate share data."""
        cache_service._redis = mock_redis
        result = await cache_service.invalidate_share_data("split-123")
        assert result is True


class TestCacheServiceClearAll:
    """Test clear all caches method."""

    @pytest.mark.asyncio
    async def test_clear_all_caches(self, cache_service, mock_redis):
        """Test clear all caches."""
        mock_redis.keys = AsyncMock(side_effect=lambda pattern: ["key1", "key2"])
        mock_redis.delete = AsyncMock(return_value=2)
        cache_service._redis = mock_redis

        result = await cache_service.clear_all_caches()
        assert "cache:split:*" in result
        assert "cache:ocr:*" in result
        assert "cache:share:*" in result
        assert "cache:session:*" in result


class TestCacheServiceStats:
    """Test cache statistics."""

    @pytest.mark.asyncio
    async def test_get_cache_stats(self, cache_service, mock_redis):
        """Test get cache statistics."""
        cache_service._redis = mock_redis

        stats = await cache_service.get_cache_stats()
        assert "connected_clients" in stats
        assert "used_memory_human" in stats
        assert "cache_hit_rate" in stats
        assert stats["cache_hit_rate"] == 80.0

    @pytest.mark.asyncio
    async def test_get_cache_stats_no_connection(self, cache_service):
        """Test get cache stats when no connection exists."""
        stats = await cache_service.get_cache_stats()
        assert "error" in stats

    @pytest.mark.asyncio
    async def test_get_cache_stats_exception(self, cache_service, mock_redis):
        """Test get cache stats with exception."""
        mock_redis.info = AsyncMock(side_effect=Exception("Redis error"))
        cache_service._redis = mock_redis

        stats = await cache_service.get_cache_stats()
        assert "error" in stats
