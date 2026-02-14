"""
Enhanced health check system for Split Bill API.
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class HealthStatus:
    """Health check status for a service."""

    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: float
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class SystemMetrics:
    """System performance metrics."""

    timestamp: datetime
    request_count: int
    error_count: int
    cache_hits: int
    cache_misses: int
    average_response_time: float
    active_connections: int


class HealthMonitor:
    """Enhanced health monitoring service."""

    def __init__(self):
        self.redis_client = None
        self.metrics_history: deque = deque(maxlen=1000)
        self._metrics_lock = asyncio.Lock()

        # Performance tracking
        self.request_times: deque = deque(maxlen=1000)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.request_counts: Dict[str, int] = defaultdict(int)

    async def initialize(self):
        """Initialize monitoring services."""
        print("✅ Health monitoring initialized")

    async def check_basic_health(self) -> Dict[str, Any]:
        """Basic health check without external dependencies."""
        start_time = time.time()

        try:
            # Basic system checks
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "api": {
                        "status": "healthy",
                        "response_time_ms": round((time.time() - start_time) * 1000, 2),
                        "last_check": datetime.now().isoformat(),
                        "details": {
                            "version": "2.0.0",
                            "python_version": "3.12+",
                            "uptime_seconds": time.time() - start_time,
                        },
                    },
                    "redis": {
                        "status": "unknown",
                        "response_time_ms": 0,
                        "last_check": datetime.now().isoformat(),
                        "error": "Redis check not implemented yet",
                    },
                    "garage": {
                        "status": "unknown",
                        "response_time_ms": 0,
                        "last_check": datetime.now().isoformat(),
                        "error": "Garage check not implemented yet",
                    },
                    "openrouter": {
                        "status": "unknown",
                        "response_time_ms": 0,
                        "last_check": datetime.now().isoformat(),
                        "error": "OpenRouter check not implemented yet",
                    },
                },
                "summary": {
                    "total_services": 4,
                    "healthy_services": 1,
                    "average_response_time_ms": round(
                        (time.time() - start_time) * 1000, 2
                    ),
                    "uptime_percentage": 25.0,
                },
            }

            return health_status

        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "services": {},
                "summary": {
                    "total_services": 0,
                    "healthy_services": 0,
                    "average_response_time_ms": 0,
                    "uptime_percentage": 0,
                },
            }

    async def record_request_metrics(
        self,
        endpoint: str,
        response_time: float,
        status_code: int,
        error: Optional[str] = None,
    ):
        """Record request metrics for monitoring."""
        async with self._metrics_lock:
            self.request_times.append(response_time)
            self.request_counts[endpoint] += 1

            if status_code >= 400 or error:
                self.error_counts[endpoint] += 1

    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        now = datetime.now()

        # Calculate average response time
        if self.request_times:
            avg_response_time = sum(self.request_times) / len(self.request_times)
        else:
            avg_response_time = 0.0

        metrics = SystemMetrics(
            timestamp=now,
            request_count=sum(self.request_counts.values()),
            error_count=sum(self.error_counts.values()),
            cache_hits=0,  # Will be implemented with Redis
            cache_misses=0,
            average_response_time=avg_response_time,
            active_connections=1,  # Simple estimation
        )

        # Store metrics history
        self.metrics_history.append(metrics)

        return metrics


# Global health monitor instance
health_monitor = HealthMonitor()
