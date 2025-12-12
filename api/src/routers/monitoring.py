"""
Simple monitoring endpoints for Split Bill API.
Provides essential health checks and metrics without excessive detail.
"""

import time
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse


# Create router
monitoring_router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@monitoring_router.get("/health")
async def simple_health_check():
    """
    Simple health check endpoint.
    Returns basic health status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "split-bill-api"
    }


@monitoring_router.get("/metrics")
async def basic_metrics():
    """
    Basic metrics endpoint.
    Returns minimal Prometheus format metrics.
    """
    return PlainTextResponse(
        "# Split Bill API Metrics\n"
        "api_uptime_seconds 0\n"
        "splits_calculated_total 0\n",
        media_type="text/plain"
    )


@monitoring_router.get("/status")
async def basic_status():
    """
    Basic application status.
    """
    return {
        "app": "split-bill-api",
        "status": "running",
        "version": "2.0.0"
    }