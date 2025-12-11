"""
Logging configuration for the application.
"""

import logging
import sys
from typing import Optional

from loguru import logger

from .config import settings


def setup_logging(log_level: Optional[str] = None, log_format: Optional[str] = None):
    """
    Configure application logging with structured output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
    """
    level = log_level or settings.LOG_LEVEL
    format_string = log_format or settings.LOG_FORMAT

    # Remove default logger
    logger.remove()

    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format=format_string,
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Add file handler for errors and above
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        format=format_string,
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        backtrace=True,
        diagnose=True,
    )

    # Configure standard library logging
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("fastapi").setLevel(level)
    logging.getLogger("httpx").setLevel(level)
    logging.getLogger("requests").setLevel(level)


def get_logger(name: str):
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logger.bind(name=name)


class LoggingContextFilter(logging.Filter):
    """Add contextual information to log records."""

    def __init__(self, context: Optional[dict] = None):
        super().__init__()
        self.context = context or {}

    def filter(self, record):
        for key, value in self.context.items():
            record.__dict__[key] = value
        return True


# Request logging middleware
async def log_request_middleware(request, call_next):
    """Log incoming requests and outgoing responses."""
    import time

    from loguru import logger

    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
    )

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 4),
    )

    return response
