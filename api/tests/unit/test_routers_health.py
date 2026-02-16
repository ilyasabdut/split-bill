"""
Unit tests for routers.health module.
Tests health check and metrics endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.routers.health import (
    health_router,
    metrics_router,
    MONITORING_DATA,
    increment_request_count,
    increment_error_count,
    increment_splits_calculated,
    increment_cache_hits,
    increment_cache_misses,
)


class TestMonitoringData:
    """Test MONITORING_DATA dictionary."""

    def test_monitoring_data_exists(self):
        """Test that MONITORING_DATA exists."""
        assert isinstance(MONITORING_DATA, dict)
        assert len(MONITORING_DATA) > 0

    def test_monitoring_data_keys(self):
        """Test MONITORING_DATA has expected keys."""
        expected_keys = [
            "request_count",
            "error_count",
            "splits_calculated",
            "cache_hits",
            "cache_misses",
            "start_time",
        ]
        for key in expected_keys:
            assert key in MONITORING_DATA

    def test_monitoring_data_initial_values(self):
        """Test MONITORING_DATA initial values."""
        assert MONITORING_DATA["request_count"] == 0
        assert MONITORING_DATA["error_count"] == 0
        assert MONITORING_DATA["splits_calculated"] == 0
        assert MONITORING_DATA["cache_hits"] == 0
        assert MONITORING_DATA["cache_misses"] == 0
        assert MONITORING_DATA["start_time"] > 0


class TestIncrementFunctions:
    """Test monitoring increment functions."""

    def test_increment_request_count(self):
        """Test increment_request_count function."""
        initial_count = MONITORING_DATA["request_count"]
        increment_request_count()
        assert MONITORING_DATA["request_count"] == initial_count + 1

    def test_increment_request_count_multiple(self):
        """Test increment_request_count multiple times."""
        initial_count = MONITORING_DATA["request_count"]
        for _ in range(5):
            increment_request_count()
        assert MONITORING_DATA["request_count"] == initial_count + 5

    def test_increment_error_count(self):
        """Test increment_error_count function."""
        initial_count = MONITORING_DATA["error_count"]
        increment_error_count()
        assert MONITORING_DATA["error_count"] == initial_count + 1

    def test_increment_splits_calculated(self):
        """Test increment_splits_calculated function."""
        initial_count = MONITORING_DATA["splits_calculated"]
        increment_splits_calculated()
        assert MONITORING_DATA["splits_calculated"] == initial_count + 1

    def test_increment_cache_hits(self):
        """Test increment_cache_hits function."""
        initial_count = MONITORING_DATA["cache_hits"]
        increment_cache_hits()
        assert MONITORING_DATA["cache_hits"] == initial_count + 1

    def test_increment_cache_misses(self):
        """Test increment_cache_misses function."""
        initial_count = MONITORING_DATA["cache_misses"]
        increment_cache_misses()
        assert MONITORING_DATA["cache_misses"] == initial_count + 1


class TestHealthCheckEndpoint:
    """Test health check endpoint."""

    def test_health_check_exists(self):
        """Test that health check endpoint exists."""
        routes = [route.path for route in health_router.routes]
        assert "/" in routes

    @pytest.mark.asyncio
    async def test_health_check_response_structure(self):
        """Test health check response structure."""
        with patch("src.routers.health.cache_service") as mock_cache:
            mock_cache._redis = AsyncMock()
            mock_cache._redis.ping = AsyncMock(return_value=True)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(health_router)
            client = TestClient(app)

            response = client.get("/health/")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data
            assert "security" in data
            assert "caching" in data
            assert "monitoring" in data

    @pytest.mark.asyncio
    async def test_health_check_cache_connected(self):
        """Test health check when cache is connected."""
        with patch("src.routers.health.cache_service") as mock_cache:
            mock_cache._redis = AsyncMock()
            mock_cache._redis.ping = AsyncMock(return_value=True)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(health_router)
            client = TestClient(app)

            response = client.get("/health/")
            data = response.json()
            assert data["cache"] == "connected"

    @pytest.mark.asyncio
    async def test_health_check_cache_error(self):
        """Test health check when cache has error."""
        with patch("src.routers.health.cache_service") as mock_cache:
            mock_cache._redis = AsyncMock()
            mock_cache._redis.ping = AsyncMock(side_effect=Exception("Redis error"))

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(health_router)
            client = TestClient(app)

            response = client.get("/health/")
            data = response.json()
            assert "error" in data["cache"]


class TestLivenessProbe:
    """Test liveness probe endpoint."""

    def test_liveness_probe_exists(self):
        """Test that liveness probe endpoint exists."""
        routes = [route.path for route in health_router.routes]
        assert "/live" in routes

    @pytest.mark.asyncio
    async def test_liveness_probe_success(self):
        """Test liveness probe returns 200."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(health_router)
        client = TestClient(app)

        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.text == "OK"


class TestReadinessProbe:
    """Test readiness probe endpoint."""

    def test_readiness_probe_exists(self):
        """Test that readiness probe endpoint exists."""
        routes = [route.path for route in health_router.routes]
        assert "/ready" in routes

    @pytest.mark.asyncio
    async def test_readiness_probe_ready(self):
        """Test readiness probe when ready."""
        with patch("src.routers.health.cache_service") as mock_cache:
            mock_cache._redis = AsyncMock()
            mock_cache._redis.ping = AsyncMock(return_value=True)

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(health_router)
            client = TestClient(app)

            response = client.get("/health/ready")
            assert response.status_code == 200
            assert response.text == "Ready"

    @pytest.mark.asyncio
    async def test_readiness_probe_not_ready(self):
        """Test readiness probe when not ready."""
        with patch("src.routers.health.cache_service") as mock_cache:
            mock_cache._redis = AsyncMock()
            mock_cache._redis.ping = AsyncMock(side_effect=Exception("Redis error"))

            from fastapi import FastAPI
            app = FastAPI()
            app.include_router(health_router)
            client = TestClient(app)

            response = client.get("/health/ready")
            assert response.status_code == 503
            data = response.json()
            assert "status" in data
            assert "error" in data


class TestMetricsEndpoint:
    """Test metrics endpoint."""

    def test_metrics_endpoint_exists(self):
        """Test that metrics endpoint exists."""
        routes = [route.path for route in metrics_router.routes]
        assert "/" in routes

    @pytest.mark.asyncio
    async def test_metrics_response_structure(self):
        """Test metrics response structure."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(metrics_router)
        client = TestClient(app)

        response = client.get("/metrics/")
        assert response.status_code == 200
        data = response.json()
        assert "application" in data
        assert "requests" in data
        assert "business" in data
        assert "cache" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_metrics_application_section(self):
        """Test metrics application section."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(metrics_router)
        client = TestClient(app)

        response = client.get("/metrics/")
        data = response.json()
        app_data = data["application"]
        assert "version" in app_data
        assert "uptime_seconds" in app_data
        assert "status" in app_data

    @pytest.mark.asyncio
    async def test_metrics_requests_section(self):
        """Test metrics requests section."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(metrics_router)
        client = TestClient(app)

        response = client.get("/metrics/")
        data = response.json()
        requests_data = data["requests"]
        assert "total" in requests_data
        assert "errors" in requests_data
        assert "error_rate" in requests_data

    @pytest.mark.asyncio
    async def test_metrics_business_section(self):
        """Test metrics business section."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(metrics_router)
        client = TestClient(app)

        response = client.get("/metrics/")
        data = response.json()
        business_data = data["business"]
        assert "splits_calculated" in business_data

    @pytest.mark.asyncio
    async def test_metrics_cache_section(self):
        """Test metrics cache section."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(metrics_router)
        client = TestClient(app)

        response = client.get("/metrics/")
        data = response.json()
        cache_data = data["cache"]
        assert "hits" in cache_data
        assert "misses" in cache_data
        assert "hit_rate" in cache_data

    @pytest.mark.asyncio
    async def test_metrics_error_rate_calculation(self):
        """Test metrics error rate calculation."""
        # Set up some errors
        MONITORING_DATA["request_count"] = 100
        MONITORING_DATA["error_count"] = 10

        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(metrics_router)
        client = TestClient(app)

        response = client.get("/metrics/")
        data = response.json()
        error_rate = data["requests"]["error_rate"]
        assert error_rate == 0.1

    @pytest.mark.asyncio
    async def test_metrics_cache_hit_rate_calculation(self):
        """Test metrics cache hit rate calculation."""
        # Set up some cache hits/misses
        MONITORING_DATA["cache_hits"] = 80
        MONITORING_DATA["cache_misses"] = 20

        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(metrics_router)
        client = TestClient(app)

        response = client.get("/metrics/")
        data = response.json()
        hit_rate = data["cache"]["hit_rate"]
        assert hit_rate == 0.8
