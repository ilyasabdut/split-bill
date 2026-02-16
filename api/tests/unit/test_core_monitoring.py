"""
Unit tests for core.monitoring module.
Tests health monitoring system.
"""


import pytest

from src.core.monitoring import (
    HealthStatus,
    SystemMetrics,
    HealthMonitor,
    health_monitor,
)


class TestHealthStatus:
    """Test HealthStatus dataclass."""

    def test_health_status_creation(self):
        """Test HealthStatus creation."""
        from datetime import datetime

        status = HealthStatus(
            name="test_service",
            status="healthy",
            response_time_ms=123.45,
            last_check=datetime.now(),
            details={"version": "1.0"},
            error=None,
        )

        assert status.name == "test_service"
        assert status.status == "healthy"
        assert status.response_time_ms == 123.45
        assert status.details == {"version": "1.0"}
        assert status.error is None

    def test_health_status_with_error(self):
        """Test HealthStatus with error."""
        from datetime import datetime

        status = HealthStatus(
            name="test_service",
            status="unhealthy",
            response_time_ms=0,
            last_check=datetime.now(),
            error="Connection failed",
        )

        assert status.error == "Connection failed"


class TestSystemMetrics:
    """Test SystemMetrics dataclass."""

    def test_system_metrics_creation(self):
        """Test SystemMetrics creation."""
        from datetime import datetime

        metrics = SystemMetrics(
            timestamp=datetime.now(),
            request_count=100,
            error_count=5,
            cache_hits=80,
            cache_misses=20,
            average_response_time=123.45,
            active_connections=10,
        )

        assert metrics.request_count == 100
        assert metrics.error_count == 5
        assert metrics.cache_hits == 80
        assert metrics.cache_misses == 20
        assert metrics.average_response_time == 123.45
        assert metrics.active_connections == 10


class TestHealthMonitorInitialization:
    """Test HealthMonitor initialization."""

    def test_health_monitor_initialization(self):
        """Test HealthMonitor initialization."""
        monitor = HealthMonitor()
        assert monitor.redis_client is None
        assert hasattr(monitor, "metrics_history")
        assert hasattr(monitor, "_metrics_lock")
        assert hasattr(monitor, "request_times")
        assert hasattr(monitor, "error_counts")
        assert hasattr(monitor, "request_counts")


class TestHealthMonitorInitialize:
    """Test HealthMonitor initialize method."""

    @pytest.mark.asyncio
    async def test_initialize(self, capsys):
        """Test initialize method."""
        monitor = HealthMonitor()
        await monitor.initialize()
        captured = capsys.readouterr()
        assert "Health monitoring initialized" in captured


class TestHealthMonitorCheckBasicHealth:
    """Test HealthMonitor check_basic_health method."""

    @pytest.mark.asyncio
    async def test_check_basic_health_success(self):
        """Test successful basic health check."""
        monitor = HealthMonitor()
        result = await monitor.check_basic_health()

        assert "status" in result
        assert "timestamp" in result
        assert "services" in result
        assert "summary" in result
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_check_basic_health_services(self):
        """Test basic health check services structure."""
        monitor = HealthMonitor()
        result = await monitor.check_basic_health()

        services = result["services"]
        assert "api" in services
        assert "redis" in services
        assert "garage" in services
        assert "openrouter" in services

    @pytest.mark.asyncio
    async def test_check_basic_health_api_service(self):
        """Test API service health check."""
        monitor = HealthMonitor()
        result = await monitor.check_basic_health()

        api_service = result["services"]["api"]
        assert api_service["status"] == "healthy"
        assert "response_time_ms" in api_service
        assert "last_check" in api_service
        assert "details" in api_service

    @pytest.mark.asyncio
    async def test_check_basic_health_summary(self):
        """Test basic health check summary."""
        monitor = HealthMonitor()
        result = await monitor.check_basic_health()

        summary = result["summary"]
        assert "total_services" in summary
        assert "healthy_services" in summary
        assert "average_response_time_ms" in summary
        assert "uptime_percentage" in summary


class TestHealthMonitorRecordRequestMetrics:
    """Test HealthMonitor record_request_metrics method."""

    @pytest.mark.asyncio
    async def test_record_request_metrics_success(self):
        """Test recording successful request metrics."""
        monitor = HealthMonitor()
        await monitor.record_request_metrics("/api/test", 123.45, 200)

        assert len(monitor.request_times) == 1
        assert monitor.request_counts["/api/test"] == 1
        assert monitor.error_counts["/api/test"] == 0

    @pytest.mark.asyncio
    async def test_record_request_metrics_error(self):
        """Test recording error request metrics."""
        monitor = HealthMonitor()
        await monitor.record_request_metrics("/api/test", 123.45, 500, "Internal error")

        assert len(monitor.request_times) == 1
        assert monitor.request_counts["/api/test"] == 1
        assert monitor.error_counts["/api/test"] == 1

    @pytest.mark.asyncio
    async def test_record_request_metrics_multiple_requests(self):
        """Test recording multiple request metrics."""
        monitor = HealthMonitor()
        await monitor.record_request_metrics("/api/test", 100.0, 200)
        await monitor.record_request_metrics("/api/test", 150.0, 200)
        await monitor.record_request_metrics("/api/other", 200.0, 500)

        assert len(monitor.request_times) == 3
        assert monitor.request_counts["/api/test"] == 2
        assert monitor.request_counts["/api/other"] == 1
        assert monitor.error_counts["/api/test"] == 0
        assert monitor.error_counts["/api/other"] == 1


class TestHealthMonitorGetSystemMetrics:
    """Test HealthMonitor get_system_metrics method."""

    @pytest.mark.asyncio
    async def test_get_system_metrics(self):
        """Test getting system metrics."""
        monitor = HealthMonitor()
        await monitor.record_request_metrics("/api/test", 100.0, 200)

        metrics = await monitor.get_system_metrics()

        assert isinstance(metrics, SystemMetrics)
        assert metrics.request_count == 1
        assert metrics.error_count == 0
        assert metrics.average_response_time == 100.0

    @pytest.mark.asyncio
    async def test_get_system_metrics_empty(self):
        """Test getting system metrics with no requests."""
        monitor = HealthMonitor()
        metrics = await monitor.get_system_metrics()

        assert metrics.request_count == 0
        assert metrics.error_count == 0
        assert metrics.average_response_time == 0.0

    @pytest.mark.asyncio
    async def test_get_system_metrics_stores_history(self):
        """Test that system metrics are stored in history."""
        monitor = HealthMonitor()
        await monitor.record_request_metrics("/api/test", 100.0, 200)

        metrics = await monitor.get_system_metrics()

        assert len(monitor.metrics_history) == 1
        assert monitor.metrics_history[0] == metrics


class TestGlobalHealthMonitorInstance:
    """Test global health_monitor instance."""

    def test_global_health_monitor_exists(self):
        """Test that global health_monitor instance exists."""
        assert health_monitor is not None
        assert isinstance(health_monitor, HealthMonitor)
