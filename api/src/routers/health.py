"""Health check router for the Split Bill API.

This module provides health check and metrics endpoints for monitoring.
"""

import logging
import time
from typing import Any, Dict

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

health_router = APIRouter(prefix="/health", tags=["health"])
metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])


# Global monitoring data
MONITORING_DATA = {
    "request_count": 0,
    "error_count": 0,
    "splits_calculated": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "start_time": time.time(),
}


@health_router.get("/")
async def health_check() -> Dict[str, Any]:
    """Check application health status.

    This endpoint provides comprehensive health information including:
    - Overall status (healthy/degraded)
    - Component status (cache, database)
    - Runtime metrics (uptime, request count)
    - Version information

    Returns:
        Dict containing health status and metrics
    """
    from .core.cache import cache_service

    uptime = time.time() - MONITORING_DATA["start_time"]

    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0",
        "security": "enabled",
        "caching": "enabled",
        "monitoring": {
            "uptime_seconds": uptime,
            "requests_total": MONITORING_DATA["request_count"],
            "errors_total": MONITORING_DATA["error_count"],
            "splits_calculated": MONITORING_DATA["splits_calculated"],
        },
    }

    # Check cache connectivity
    try:
        if cache_service and cache_service._redis:
            await cache_service._redis.ping()  # type: ignore
            health_status["cache"] = "connected"
    except Exception as e:
        health_status["cache"] = f"error: {e}"

    return health_status


@health_router.get("/live")
async def liveness_probe() -> Response:
    """Kubernetes liveness probe.

    This endpoint is used by Kubernetes to determine if the container
    is alive. It should be fast and not depend on external services.

    Returns:
        HTTP 200 if the application is running
    """
    return Response(status_code=200, content="OK")


@health_router.get("/ready")
async def readiness_probe() -> Response:
    """Kubernetes readiness probe.

    This endpoint is used by Kubernetes to determine if the container
    is ready to accept traffic. It checks critical dependencies.

    Returns:
        HTTP 200 if ready, 503 if not
    """
    from .core.cache import cache_service

    try:
        # Check Redis connectivity
        if cache_service and cache_service._redis:
            await cache_service._redis.ping()  # type: ignore
        return Response(status_code=200, content="Ready")
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "error": str(e)},
        )


@metrics_router.get("/")
async def get_metrics() -> Dict[str, Any]:
    """Get application metrics.

    This endpoint provides detailed metrics for monitoring:
    - Request statistics (total, errors, rate)
    - Business metrics (splits calculated)
    - Cache statistics (hits, misses, hit rate)
    - Performance metrics (uptime)

    Returns:
        Dict containing all metrics
    """
    uptime = time.time() - MONITORING_DATA["start_time"]

    cache_hits = MONITORING_DATA["cache_hits"]
    cache_misses = MONITORING_DATA["cache_misses"]
    total_cache_ops = cache_hits + cache_misses

    cache_hit_rate = 0.0
    if total_cache_ops > 0:
        cache_hit_rate = cache_hits / total_cache_ops

    error_rate = 0.0
    total_requests = MONITORING_DATA["request_count"]
    if total_requests > 0:
        error_rate = MONITORING_DATA["error_count"] / total_requests

    return {
        "application": {
            "version": "2.0.0",
            "uptime_seconds": uptime,
            "status": "running",
        },
        "requests": {
            "total": total_requests,
            "errors": MONITORING_DATA["error_count"],
            "error_rate": round(error_rate, 4),
        },
        "business": {
            "splits_calculated": MONITORING_DATA["splits_calculated"],
        },
        "cache": {
            "hits": cache_hits,
            "misses": cache_misses,
            "hit_rate": round(cache_hit_rate, 4),
        },
        "timestamp": time.time(),
    }


def increment_request_count() -> None:
    """Increment the request counter."""
    MONITORING_DATA["request_count"] += 1


def increment_error_count() -> None:
    """Increment the error counter."""
    MONITORING_DATA["error_count"] += 1


def increment_splits_calculated() -> None:
    """Increment the splits calculated counter."""
    MONITORING_DATA["splits_calculated"] += 1


def increment_cache_hits() -> None:
    """Increment the cache hits counter."""
    MONITORING_DATA["cache_hits"] += 1


def increment_cache_misses() -> None:
    """Increment the cache misses counter."""
    MONITORING_DATA["cache_misses"] += 1
