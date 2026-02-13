"""
Redis cache service for performance optimization.
Provides caching for split results, OCR processing, and share data.
"""

import json
import logging
import os
from datetime import timedelta
from typing import Any, Dict, Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# Get Redis URL from environment
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


class CacheService:
    """Redis-based cache service for the application."""

    def __init__(self):
        self.redis_url = REDIS_URL
        self._redis: Optional[Redis] = None
        self._connection_pool = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self._redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Test connection
            pong: bool = await self._redis.ping()  # type: ignore
            if pong:
                logger.info("Connected to Redis cache successfully")
            else:
                raise RuntimeError("Redis ping failed")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._redis = None
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Disconnected from Redis cache")

    async def get_redis(self) -> Optional[Redis]:
        """Get Redis connection, creating one if needed."""
        if self._redis is None:
            await self.connect()
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            redis_client = await self.get_redis()
            if not redis_client:
                return None

            value = await redis_client.get(key)
            if value is None:
                return None

            return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[timedelta] = None,
        expire_seconds: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time as timedelta
            expire_seconds: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            redis_client = await self.get_redis()
            if not redis_client:
                return False

            serialized_value = json.dumps(value, default=str)

            if expire:
                result = await redis_client.setex(
                    key, int(expire.total_seconds()), serialized_value
                )
            elif expire_seconds:
                result = await redis_client.setex(key, expire_seconds, serialized_value)
            else:
                result = await redis_client.set(key, serialized_value)

            return bool(result)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            redis_client = await self.get_redis()
            if not redis_client:
                return False

            result = await redis_client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        try:
            redis_client = await self.get_redis()
            if not redis_client:
                return False

            result = await redis_client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "cache:split:*")

        Returns:
            Number of keys deleted
        """
        try:
            redis_client = await self.get_redis()
            if not redis_client:
                return 0

            keys = await redis_client.keys(pattern)
            if keys:
                return await redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0

    async def get_ttl(self, key: str) -> int:
        """
        Get TTL (time to live) for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds (-1 if no expiration, -2 if key doesn't exist)
        """
        try:
            redis_client = await self.get_redis()
            if not redis_client:
                return -2

            return await redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -2

    # Cache key generators
    def split_result_key(self, split_id: str) -> str:
        """Generate cache key for split result."""
        return f"cache:split:result:{split_id}"

    def ocr_result_key(self, image_hash: str) -> str:
        """Generate cache key for OCR result."""
        return f"cache:ocr:result:{image_hash}"

    def share_data_key(self, split_id: str) -> str:
        """Generate cache key for share data."""
        return f"cache:share:data:{split_id}"

    def user_session_key(self, session_id: str) -> str:
        """Generate cache key for user session."""
        return f"cache:session:{session_id}"

    # Specific cache methods
    async def get_split_result(self, split_id: str) -> Optional[Dict[str, Any]]:
        """Get cached split calculation result."""
        key = self.split_result_key(split_id)
        return await self.get(key)

    async def set_split_result(
        self,
        split_id: str,
        result: Dict[str, Any],
        expire_hours: int = 1,
    ) -> bool:
        """Cache split calculation result with 1-hour expiration."""
        key = self.split_result_key(split_id)
        expire = timedelta(hours=expire_hours)
        return await self.set(key, result, expire=expire)

    async def get_ocr_result(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached OCR processing result."""
        key = self.ocr_result_key(image_hash)
        return await self.get(key)

    async def set_ocr_result(
        self,
        image_hash: str,
        ocr_result: Dict[str, Any],
        expire_minutes: int = 30,
    ) -> bool:
        """Cache OCR processing result with 30-minute expiration."""
        key = self.ocr_result_key(image_hash)
        expire = timedelta(minutes=expire_minutes)
        return await self.set(key, ocr_result, expire=expire)

    async def get_share_data(self, split_id: str) -> Optional[Dict[str, Any]]:
        """Get cached share data."""
        key = self.share_data_key(split_id)
        return await self.get(key)

    async def set_share_data(
        self,
        split_id: str,
        share_data: Dict[str, Any],
        expire_hours: int = 24,
    ) -> bool:
        """Cache share data with 24-hour expiration."""
        key = self.share_data_key(split_id)
        expire = timedelta(hours=expire_hours)
        return await self.set(key, share_data, expire=expire)

    # Cache invalidation methods
    async def invalidate_split_result(self, split_id: str) -> bool:
        """Invalidate cached split result."""
        key = self.split_result_key(split_id)
        return await self.delete(key)

    async def invalidate_share_data(self, split_id: str) -> bool:
        """Invalidate cached share data."""
        key = self.share_data_key(split_id)
        return await self.delete(key)

    async def invalidate_ocr_result(self, image_hash: str) -> bool:
        """Invalidate cached OCR result."""
        key = self.ocr_result_key(image_hash)
        return await self.delete(key)

    async def clear_all_caches(self) -> Dict[str, int]:
        """Clear all application caches."""
        patterns = [
            "cache:split:*",
            "cache:ocr:*",
            "cache:share:*",
            "cache:session:*",
        ]

        results = {}
        for pattern in patterns:
            deleted_count = await self.clear_pattern(pattern)
            results[pattern] = deleted_count

        logger.info(f"Cleared caches: {results}")
        return results

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            redis_client = await self.get_redis()
            if not redis_client:
                return {"error": "Redis not connected"}

            info = await redis_client.info()

            stats = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "cache_hit_rate": 0,
            }

            # Calculate hit rate
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            if hits + misses > 0:
                stats["cache_hit_rate"] = round((hits / (hits + misses)) * 100, 2)

            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Global cache service instance
cache_service = CacheService()
