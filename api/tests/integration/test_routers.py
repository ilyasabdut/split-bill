"""Integration tests for API routers."""

import pytest
from fastapi.testclient import TestClient


class TestSplitsRouter:
    """Integration tests for /splits endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.main import app

        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_calculate_split_requires_auth(self, client):
        """Test that calculate endpoint requires authentication."""
        response = client.post(
            "/splits/calculate",
            json={
                "person_names": ["Alice", "Bob"],
                "item_assignments": [],
                "tax_amount_input": 2.50,
                "tip_amount_input": 5.00,
                "split_evenly": False,
                "extracted_total_discount": 0.0,
                "original_parsed_data": {},
            },
        )
        assert response.status_code in (401, 403)

    def test_calculate_split_with_auth(self, client):
        """Test calculate split with valid auth."""
        response = client.post(
            "/splits/calculate",
            json={
                "person_names": ["Alice", "Bob"],
                "item_assignments": [
                    {
                        "item_details": {"item": "Burger", "price": 10.00},
                        "assigned_to": ["Alice", "Bob"],
                    }
                ],
                "tax_amount_input": 1.00,
                "tip_amount_input": 2.00,
                "split_evenly": False,
                "extracted_total_discount": 0.0,
                "original_parsed_data": {},
            },
            headers={"Authorization": "Bearer test-key-123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "split_results" in data
        assert "share_link" in data
        assert "split_id" in data

    def test_view_split_requires_auth(self, client):
        """Test that view endpoint requires authentication."""
        response = client.get("/splits/view/test123")
        assert response.status_code in (401, 403)


class TestReceiptsRouter:
    """Integration tests for /receipts endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.main import app

        return TestClient(app)

    def test_upload_receipt_requires_auth(self, client):
        """Test that upload endpoint requires authentication."""
        response = client.post(
            "/receipts/upload",
            files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
        )
        assert response.status_code in (401, 403)


class TestCorrelationId:
    """Tests for correlation ID middleware."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.main import app

        return TestClient(app)

    def test_correlation_id_in_response(self, client):
        """Test that correlation ID is added to response headers."""
        response = client.get("/")
        assert response.status_code == 200
        # Correlation ID should be in response headers
        assert "X-Correlation-ID" in response.headers

    def test_custom_correlation_id_preserved(self, client):
        """Test that custom correlation ID is preserved."""
        custom_id = "test-correlation-123"
        response = client.get(
            "/",
            headers={"X-Correlation-ID": custom_id},
        )
        assert response.status_code == 200
        assert response.headers.get("X-Correlation-ID") == custom_id
