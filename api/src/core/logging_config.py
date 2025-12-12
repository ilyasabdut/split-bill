"""
Structured logging configuration for Split Bill API.
Provides JSON-based logging with correlation IDs and performance tracking.
"""

import logging
import os
import time
import uuid
from contextvars import ContextVar
from functools import wraps
from typing import Any, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variables for correlation IDs
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs to requests."""

    async def dispatch(self, request: Request, call_next):
        # Generate or extract correlation ID
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        correlation_id.set(corr_id)

        # Add to request state for access in route handlers
        request.state.correlation_id = corr_id

        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = corr_id

        return response


class LoggingContextFilter(logging.Filter):
    """Filter to add context information to log records."""

    def filter(self, record):
        record.correlation_id = correlation_id.get() or "no-correlation-id"
        return True


def setup_standard_logging():
    """Set up standard logging with enhanced formatting."""
    # Configure standard logging
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=logging.INFO,
    )

    # Add correlation ID filter
    root_logger = logging.getLogger()
    correlation_filter = LoggingContextFilter()
    for handler in root_logger.handlers:
        handler.addFilter(correlation_filter)

    return logging.getLogger(__name__)


# Initialize logger
logger = setup_standard_logging()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name or __name__)


def log_request(
    logger_instance: logging.Logger,
    request: Request,
    response: Response,
    duration_ms: float,
):
    """Log request details with structured format."""
    logger_instance.info(
        "HTTP Request - Method: %s, Path: %s, Status: %d, Duration: %.2fms, User-Agent: %s, IP: %s, Correlation: %s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request.headers.get("user-agent"),
        request.client.host if request.client else None,
        correlation_id.get(),
    )


def log_error(
    logger_instance: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
):
    """Log error with context."""
    error_context = context or {}
    error_context.update(
        {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "correlation_id": correlation_id.get(),
        }
    )

    logger_instance.error(
        "Application Error - Type: %s, Message: %s, Context: %s",
        error_context["error_type"],
        error_context["error_message"],
        str(error_context),
    )


def log_performance(
    logger_instance: logging.Logger,
    operation: str,
    duration_ms: float,
    context: Optional[Dict[str, Any]] = None,
):
    """Log performance metrics."""
    perf_context = context or {}
    perf_context.update(
        {
            "operation": operation,
            "duration_ms": duration_ms,
            "correlation_id": correlation_id.get(),
        }
    )

    logger_instance.info(
        "Performance Metric - Operation: %s, Duration: %.2fms, Context: %s",
        operation,
        duration_ms,
        str(perf_context),
    )


def log_security_event(
    logger_instance: logging.Logger,
    event_type: str,
    details: Optional[Dict[str, Any]] = None,
):
    """Log security-related events."""
    security_context = details or {}
    security_context.update(
        {
            "event_type": "security",
            "security_event": event_type,
            "correlation_id": correlation_id.get(),
        }
    )

    logger_instance.warning(
        "Security Event - Type: %s, Details: %s", event_type, str(security_context)
    )


def performance_monitor(operation_name: Optional[str] = None):
    """Decorator to monitor function performance."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                log_performance(
                    logger,
                    op_name,
                    duration_ms,
                    {"status": "success", "function": func.__name__},
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                log_error(
                    logger,
                    e,
                    {
                        "operation": op_name,
                        "duration_ms": duration_ms,
                        "status": "error",
                    },
                )

                raise

        return wrapper

    return decorator


def request_monitor(operation_name: Optional[str] = None):
    """Decorator to monitor API request performance."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__name__}"
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                # Record metrics in health monitor
                try:
                    from core.monitoring import health_monitor

                    await health_monitor.record_request_metrics(
                        endpoint=op_name, response_time=duration_ms, status_code=200
                    )
                except ImportError:
                    pass  # Health monitor might not be available

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                # Record error metrics
                try:
                    from core.monitoring import health_monitor

                    await health_monitor.record_request_metrics(
                        endpoint=op_name,
                        response_time=duration_ms,
                        status_code=500,
                        error=str(e),
                    )
                except ImportError:
                    pass

                raise

        return wrapper

    return decorator


class LoggingConfig:
    """Configuration for logging system."""

    def __init__(self):
        self.correlation_id_header = "X-Correlation-ID"
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.enable_performance_logging = True
        self.enable_security_logging = True
