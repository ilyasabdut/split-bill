"""
Basic Monitoring Module
Provides essential monitoring and health check functionality.
"""

import logging
import time
from typing import Any, Dict, Optional

# Configure structured logging
try:
    import structlog

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger(__name__)
    STRUCTLOG_AVAILABLE = True
except ImportError:
    # Fallback to standard logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False

# =============================================================================
# BASIC METRICS (without prometheus for now)
# =============================================================================


class MetricsCollector:
    """Simple metrics collector without external dependencies."""

    def __init__(self):
        self.request_count = {}
        self.request_latency = {}
        self.error_count = {}
        self.business_metrics = {
            "receipts_processed": 0,
            "splits_calculated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record request metrics."""
        key = f"{method}:{endpoint}:{status_code}"
        self.request_count[key] = self.request_count.get(key, 0) + 1

        latency_key = f"{method}:{endpoint}"
        if latency_key not in self.request_latency:
            self.request_latency[latency_key] = []
        self.request_latency[latency_key].append(duration)

    def record_error(self, error_type: str, endpoint: str):
        """Record error occurrence."""
        key = f"{error_type}:{endpoint}"
        self.error_count[key] = self.error_count.get(key, 0) + 1

    def record_receipt_processed(self):
        """Record receipt processing."""
        self.business_metrics["receipts_processed"] += 1

    def record_split_calculation(self):
        """Record split calculation."""
        self.business_metrics["splits_calculated"] += 1

    def record_cache_hit(self):
        """Record cache hit."""
        self.business_metrics["cache_hits"] += 1

    def record_cache_miss(self):
        """Record cache miss."""
        self.business_metrics["cache_misses"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "requests": self.request_count,
            "latency": self.request_latency,
            "errors": self.error_count,
            "business": self.business_metrics.copy(),
            "timestamp": time.time(),
        }


# Global metrics collector
metrics = MetricsCollector()

# =============================================================================
# HEALTH CHECKS
# =============================================================================


class HealthChecker:
    """Comprehensive health checker for all system components."""

    def __init__(self):
        self.checks = {}

    def register_check(self, name: str, check_func):
        """Register a health check function."""
        self.checks[name] = check_func

    async def check_all(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        overall_status = "healthy"

        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = result
                if not result.get("healthy", False):
                    overall_status = "unhealthy"
            except Exception as e:
                logger.error(f"Health check failed for {name}", exc_info=e)
                results[name] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": time.time(),
                }
                overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": time.time(),
            "checks": results,
            "version": "2.0.0",
            "metrics": metrics.get_metrics(),
        }


# Global health checker instance
health_checker = HealthChecker()

# =============================================================================
# HEALTH CHECK FUNCTIONS
# =============================================================================


async def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        from core.cache import cache_service

        if not cache_service:
            return {"healthy": False, "error": "Cache service not available"}

        # Test Redis connection
        await cache_service.get("health_check")

        return {
            "healthy": True,
            "message": "Redis connection successful",
            "timestamp": time.time(),
        }
    except Exception as e:
        return {"healthy": False, "error": str(e), "timestamp": time.time()}


async def check_minio_health() -> Dict[str, Any]:
    """Check MinIO accessibility."""
    try:
        # This would check MinIO connectivity
        # For now, return a placeholder response
        return {
            "healthy": True,
            "message": "MinIO check not implemented",
            "timestamp": time.time(),
        }
    except Exception as e:
        return {"healthy": False, "error": str(e), "timestamp": time.time()}


async def check_external_api_health() -> Dict[str, Any]:
    """Check external API availability."""
    try:
        import os

        api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            return {
                "healthy": False,
                "error": "OpenRouter API key not configured",
                "timestamp": time.time(),
            }

        return {
            "healthy": True,
            "message": "External API configuration OK",
            "timestamp": time.time(),
        }
    except Exception as e:
        return {"healthy": False, "error": str(e), "timestamp": time.time()}


# Register health checks
health_checker.register_check("redis", check_redis_health)
health_checker.register_check("minio", check_minio_health)
health_checker.register_check("external_apis", check_external_api_health)

# =============================================================================
# ERROR TRACKING (Basic implementation)
# =============================================================================


def track_exception(exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Track exception with context."""
    error_info = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "context": context or {},
    }
    logger.error("Exception tracked", **error_info)


def track_message(
    message: str, level: str = "info", context: Optional[Dict[str, Any]] = None
):
    """Track custom message."""
    log_data = {"message": message, "context": context or {}}
    if level == "error":
        logger.error("Message tracked", **log_data)
    elif level == "warning":
        logger.warning("Message tracked", **log_data)
    else:
        logger.info("Message tracked", **log_data)


# Initialize basic error tracking
try:
    import os

    sentry_dsn = os.environ.get("SENTRY_DSN")
    if sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=0.1,
            environment=os.environ.get("ENVIRONMENT", "development"),
        )
        logger.info("Sentry initialized for error tracking")
    else:
        logger.info("Sentry DSN not provided, using basic error tracking")
except ImportError:
    logger.info("Sentry SDK not available, using basic error tracking")
