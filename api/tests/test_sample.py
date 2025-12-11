"""
Sample test file to demonstrate the testing structure.
"""

import os
import sys

import pytest

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.split_logic import calculate_split


class TestSplitLogic:
    """Test cases for split logic functionality."""

    def test_calculate_split_even_split(self):
        """Test even split calculation."""
        result = calculate_split(
            assignments=[],
            tax_amount_str="2.00",
            tip_amount_str="3.00",
            person_names=["Alice", "Bob"],
            split_evenly_flag=True,
            overall_subtotal_for_even_split=20.00,
        )

        # Verify results
        assert "Alice" in result
        assert "Bob" in result
        assert result["Alice"]["subtotal"] == 10.00
        assert result["Bob"]["subtotal"] == 10.00
        assert result["Alice"]["total"] == 12.50
        assert result["Bob"]["total"] == 12.50

    def test_calculate_split_with_discount(self):
        """Test split calculation with discount."""
        result = calculate_split(
            assignments=[],
            tax_amount_str="2.00",
            tip_amount_str="3.00",
            person_names=["Alice", "Bob"],
            split_evenly_flag=True,
            overall_subtotal_for_even_split=20.00,
            total_discount_amount=5.00,
        )

        # Verify discount is applied
        expected_subtotal = (20.00 - 5.00) / 2  # 7.50 each
        assert result["Alice"]["subtotal"] == expected_subtotal
        assert result["Bob"]["subtotal"] == expected_subtotal


class TestHealthEndpoint:
    """Test cases for health endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        from api_main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
