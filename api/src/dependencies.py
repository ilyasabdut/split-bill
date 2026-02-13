"""Shared dependencies for the Split Bill API.

This module provides reusable dependencies for authentication,
rate limiting, and other cross-cutting concerns.
"""

import logging
import os
import time
from collections import defaultdict
from functools import wraps
from typing import Any, Callable, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Get API key from environment
API_KEY = os.environ.get("API_KEY", "default-dev-key-123")


async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify API key from Bearer token.

    This dependency validates the API key provided in the Authorization header.
    It ensures that all protected endpoints require valid authentication.

    Args:
        credentials: HTTP Bearer credentials from the request

    Returns:
        str: The validated API key

    Raises:
        HTTPException: If authentication fails (401 Unauthorized)
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use Bearer.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


class SimpleRateLimiter:
    """Simple in-memory rate limiter for API endpoints.

    This rate limiter tracks requests per client IP within a sliding window.
    It's suitable for single-instance deployments but should be replaced
    with Redis-based rate limiting for multi-instance deployments.

    Attributes:
        requests: Dictionary tracking request timestamps per client
        default_limit: Default rate limit (requests per window)
        default_window: Default time window in seconds
    """

    def __init__(
        self,
        default_limit: int = 30,
        default_window: int = 60,
    ):
        self.requests: Dict[str, list[float]] = defaultdict(list)
        self.default_limit = default_limit
        self.default_window = default_window

    def is_rate_limited(
        self,
        client_id: str,
        limit: Optional[int] = None,
        window: Optional[int] = None,
    ) -> tuple[bool, Optional[int]]:
        """Check if client is rate limited.

        Args:
            client_id: Unique identifier for the client (usually IP address)
            limit: Maximum requests allowed in the window
            window: Time window in seconds

        Returns:
            tuple: (is_limited, retry_after_seconds)
        """
        limit = limit or self.default_limit
        window = window or self.default_window
        now = time.time()

        # Clean old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] if now - req_time < window
        ]

        # Check if over limit
        if len(self.requests[client_id]) >= limit:
            # Calculate retry-after based on oldest request
            oldest = min(self.requests[client_id])
            retry_after = int(window - (now - oldest))
            return True, max(1, retry_after)

        # Add current request
        self.requests[client_id].append(now)
        return False, None

    def get_usage(self, client_id: str) -> dict[str, Any]:
        """Get current usage statistics for a client.

        Args:
            client_id: Unique identifier for the client

        Returns:
            dict: Usage statistics including request count and remaining requests
        """
        now = time.time()
        window = self.default_window
        requests = self.requests.get(client_id, [])

        # Clean old requests
        valid_requests = [r for r in requests if now - r < window]

        return {
            "requests_in_window": len(valid_requests),
            "limit": self.default_limit,
            "remaining": max(0, self.default_limit - len(valid_requests)),
            "window_seconds": window,
        }


# Global rate limiter instance
rate_limiter = SimpleRateLimiter()


def rate_limit(requests_per_minute: int):
    """Rate limiting decorator for endpoints.

    This decorator limits the number of requests a client can make
    within a one-minute window. It uses in-memory storage and is suitable
    for single-instance deployments.

    Args:
        requests_per_minute: Maximum requests allowed per minute

    Returns:
        callable: Decorated function with rate limiting

    Example:
        @app.post("/endpoint")
        @rate_limit(30)
        async def my_endpoint():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract request from kwargs or args
            request: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)

            client_ip = request.client.host if request.client else "unknown"

            is_limited, retry_after = rate_limiter.is_rate_limited(
                client_id=client_ip,
                limit=requests_per_minute,
                window=60,
            )

            if is_limited:
                logger.warning(
                    f"Rate limit exceeded for {client_ip}: "
                    f"{requests_per_minute} requests/minute"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {requests_per_minute} requests per minute.",
                    headers={"Retry-After": str(retry_after or 60)},
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def get_current_client_ip(request: Request) -> str:
    """Extract client IP address from request.

    This function handles proxied requests by checking X-Forwarded-For header
    first, then falling back to direct client address.

    Args:
        request: FastAPI request object

    Returns:
        str: Client IP address
    """
    # Check for forwarded header (when behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()

    # Fall back to direct connection
    return request.client.host if request.client else "unknown"


# Common dependency injection patterns
async def get_rate_limiter() -> SimpleRateLimiter:
    """Get the rate limiter instance.

    This dependency can be used when you need access to the rate limiter
    for custom rate limiting logic.

    Returns:
        SimpleRateLimiter: The global rate limiter instance
    """
    return rate_limiter
