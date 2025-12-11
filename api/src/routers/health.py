"""
Health check router for monitoring API status.
"""

import time
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    """Simple health status response."""

    status: str = "healthy"
    timestamp: str = datetime.utcnow().isoformat()
    version: str = "1.0.0"
    uptime_seconds: float


@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        Health status information
    """
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        uptime_seconds=time.time(),  # This would normally be calculated from start time
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes/container orchestration.

    Returns:
        Simple readiness status
    """
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}


@router.get("/live")
async def liveness_check():
    """
    Liveness probe for Kubernetes/container orchestration.

    Returns:
        Simple liveness status
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
