"""
Unit tests for routers.monitoring module.
Tests simple monitoring endpoints.
"""

from fastapi.testclient import TestClient

from src.routers.monitoring import monitoring_router


class TestMonitoringRouter:
    """Test monitoring router."""

    def test_monitoring_router_exists(self):
        """Test that monitoring router exists."""
        assert monitoring_router is not None
        assert monitoring_router.prefix == "/monitoring"


class TestSimpleHealthCheck:
    """Test simple health check endpoint."""

    def test_simple_health_check_exists(self):
        """Test that simple health check endpoint exists."""
        routes = [route.path for route in monitoring_router.routes]
        assert "/health" in routes

    def test_simple_health_check_response(self):
        """Test simple health check response."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(monitoring_router)
        client = TestClient(app)

        response = client.get("/monitoring/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "service" in data

    def test_simple_health_check_status(self):
        """Test simple health check status value."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(monitoring_router)
        client = TestClient(app)

        response = client.get("/monitoring/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_simple_health_check_service_name(self):
        """Test simple health check service name."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(monitoring_router)
        client = TestClient(app)

        response = client.get("/monitoring/health")
        data = response.json()
        assert data["service"] == "split-bill-api"


class TestBasicMetrics:
    """Test basic metrics endpoint."""

    def test_basic_metrics_exists(self):
        """Test that basic metrics endpoint exists."""
        routes = [route.path for route in monitoring_router.routes]
        assert "/metrics" in routes

    def test_basic_metrics_response(self):
        """Test basic metrics response."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(monitoring_router)
        client = TestClient(app)

        response = client.get("/monitoring/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")

    def test_basic_metrics_content(self):
        """Test basic metrics content."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(monitoring_router)
        client = TestClient(app)

        response = client.get("/monitoring/metrics")
        content = response.text
        assert "Split Bill API Metrics" in content
        assert "api_uptime_seconds" in content
        assert "splits_calculated_total" in content


class TestBasicStatus:
    """Test basic status endpoint."""

    def test_basic_status_exists(self):
        """Test that basic status endpoint exists."""
        routes = [route.path for route in monitoring_router.routes]
        assert "/status" in routes

    def test_basic_status_response(self):
        """Test basic status response."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(monitoring_router)
        client = TestClient(app)

        response = client.get("/monitoring/status")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "status" in data
        assert "version" in data

    def test_basic_status_values(self):
        """Test basic status values."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(monitoring_router)
        client = TestClient(app)

        response = client.get("/monitoring/status")
        data = response.json()
        assert data["app"] == "split-bill-api"
        assert data["status"] == "running"
        assert data["version"] == "2.0.0"


class TestRouterTags:
    """Test router tags."""

    def test_monitoring_router_tags(self):
        """Test monitoring router tags."""
        assert monitoring_router.tags == ["monitoring"]
