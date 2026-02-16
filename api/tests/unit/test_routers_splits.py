"""
Unit tests for routers.splits module.
Tests split calculation and viewing endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.routers.splits import (
    splits_router,
    calculate_split,
)
from src.models.schemas import (
    CalculateSplitRequest,
    CalculateSplitResponse,
    SharedSplitDataResponse,
)


class TestSplitsRouter:
    """Test splits router."""

    def test_splits_router_exists(self):
        """Test that splits router exists."""
        assert splits_router is not None
        assert splits_router.prefix == "/splits"

    def test_splits_router_tags(self):
        """Test splits router tags."""
        assert splits_router.tags == ["splits"]


class TestCalculateSplitFunction:
    """Test calculate_split function."""

    def test_calculate_split_even_split(self):
        """Test calculate_split with even split."""
        person_names = ["Alice", "Bob", "Charlie"]
        result = calculate_split(
            item_assignments=[],
            tax_str="10.0",
            tip_str="5.0",
            person_names=person_names,
            split_evenly_flag=True,
            overall_subtotal_for_even_split=90.0,
            total_discount_amount=0.0,
        )

        assert "Alice" in result
        assert "Bob" in result
        assert "Charlie" in result
        # Each person should get equal share of subtotal
        assert result["Alice"]["subtotal"] == 30.0
        assert result["Bob"]["subtotal"] == 30.0
        assert result["Charlie"]["subtotal"] == 30.0

    def test_calculate_split_individual_assignment(self):
        """Test calculate_split with individual item assignment."""
        person_names = ["Alice", "Bob"]
        item_assignments = [
            {
                "item_details": {"item": "Pizza", "price": 20.0},
                "assigned_to": ["Alice", "Bob"],
            },
            {
                "item_details": {"item": "Salad", "price": 10.0},
                "assigned_to": ["Alice"],
            },
        ]

        result = calculate_split(
            item_assignments=item_assignments,
            tax_str="5.0",
            tip_str="2.0",
            person_names=person_names,
            split_evenly_flag=False,
        )

        # Alice gets half of pizza (10) + full salad (10) = 20
        assert result["Alice"]["subtotal"] == 20.0
        # Bob gets half of pizza (10)
        assert result["Bob"]["subtotal"] == 10.0

    def test_calculate_split_with_tax_and_tip(self):
        """Test calculate_split with tax and tip."""
        person_names = ["Alice", "Bob"]
        item_assignments = [
            {
                "item_details": {"item": "Pizza", "price": 20.0},
                "assigned_to": ["Alice"],
            },
        ]

        result = calculate_split(
            item_assignments=item_assignments,
            tax_str="5.0",  # 25% of 20 = 5
            tip_str="2.0",  # 10% of 20 = 2
            person_names=person_names,
            split_evenly_flag=False,
        )

        # Alice gets pizza (20) + tax (5) + tip (2) = 27
        assert result["Alice"]["subtotal"] == 20.0
        assert result["Alice"]["tax"] == 5.0
        assert result["Alice"]["tip"] == 2.0
        assert result["Alice"]["total"] == 27.0

    def test_calculate_split_no_people(self):
        """Test calculate_split with no people."""
        result = calculate_split(
            item_assignments=[],
            tax_str="0",
            tip_str="0",
            person_names=[],
            split_evenly_flag=False,
        )

        assert result == {}

    def test_calculate_split_invalid_tax_tip(self):
        """Test calculate_split with invalid tax/tip values."""
        person_names = ["Alice", "Bob"]
        item_assignments = [
            {
                "item_details": {"item": "Pizza", "price": 20.0},
                "assigned_to": ["Alice"],
            },
        ]

        # Should handle invalid tax/tip gracefully
        result = calculate_split(
            item_assignments=item_assignments,
            tax_str="invalid",
            tip_str="also_invalid",
            person_names=person_names,
            split_evenly_flag=False,
        )

        assert "Alice" in result
        # Tax and tip should default to 0.0
        assert result["Alice"]["tax"] == 0.0
        assert result["Alice"]["tip"] == 0.0

    def test_calculate_split_zero_subtotal(self):
        """Test calculate_split with zero subtotal."""
        person_names = ["Alice", "Bob"]
        item_assignments = []

        result = calculate_split(
            item_assignments=item_assignments,
            tax_str="10.0",
            tip_str="5.0",
            person_names=person_names,
            split_evenly_flag=False,
        )

        # Tax and tip should be divided equally
        assert result["Alice"]["tax"] == 5.0
        assert result["Alice"]["tip"] == 2.5
        assert result["Bob"]["tax"] == 5.0
        assert result["Bob"]["tip"] == 2.5


class TestCalculateSplitRequest:
    """Test CalculateSplitRequest model."""

    def test_calculate_split_request_creation(self):
        """Test CalculateSplitRequest creation."""
        request = CalculateSplitRequest(
            person_names=["Alice", "Bob"],
            item_assignments=[],
            tax_amount_input="10.0",
            tip_amount_input="5.0",
            split_evenly=False,
            extracted_subtotal_from_gemini=100.0,
            extracted_total_discount=0.0,
        )

        assert request.person_names == ["Alice", "Bob"]
        assert request.tax_amount_input == "10.0"
        assert request.tip_amount_input == "5.0"
        assert request.split_evenly is False

    def test_calculate_split_request_defaults(self):
        """Test CalculateSplitRequest with defaults."""
        request = CalculateSplitRequest(
            person_names=["Alice"],
            item_assignments=[],
        )

        assert request.tax_amount_input is None
        assert request.tip_amount_input is None
        assert request.split_evenly is False
        assert request.extracted_subtotal_from_gemini is None


class TestCalculateSplitResponse:
    """Test CalculateSplitResponse model."""

    def test_calculate_split_response_creation(self):
        """Test CalculateSplitResponse creation."""
        split_results = {"Alice": {"total": 25.0}}
        response = CalculateSplitResponse(
            split_results=split_results,
            share_link="http://example.com/splits/view/abc123",
            split_id="abc123",
        )

        assert response.split_results == split_results
        assert response.share_link == "http://example.com/splits/view/abc123"
        assert response.split_id == "abc123"


class TestSharedSplitDataResponse:
    """Test SharedSplitDataResponse model."""

    def test_shared_split_data_response_creation(self):
        """Test SharedSplitDataResponse creation."""
        response = SharedSplitDataResponse(
            split_id="abc123",
            original_parsed_data={"items": []},
            person_names=["Alice", "Bob"],
            item_assignments=[],
            split_evenly_choice=False,
            total_discount_applied=0.0,
            user_adjusted_tax=2.0,
            user_adjusted_tip=5.0,
            calculated_split_results={"Alice": {"total": 25.0}},
            creation_timestamp=1234567890.0,
        )

        assert response.split_id == "abc123"
        assert response.person_names == ["Alice", "Bob"]
        assert response.split_evenly_choice is False
        assert response.user_adjusted_tax == 2.0
        assert response.user_adjusted_tip == 5.0


class TestCalculateSplitEndpoint:
    """Test calculate_split_endpoint."""

    def test_calculate_split_endpoint_exists(self):
        """Test that calculate endpoint exists."""
        routes = [route.path for route in splits_router.routes]
        assert "/calculate" in routes

    @pytest.mark.asyncio
    async def test_calculate_split_no_people(self):
        """Test calculate endpoint with no people raises error."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(splits_router)
        client = TestClient(app)

        with patch("src.routers.splits.get_api_key", return_value="test-key"):
            request_data = {
                "person_names": [],
                "item_assignments": [],
                "tax_amount_input": "0",
                "tip_amount_input": "0",
                "split_evenly": False,
            }

            response = client.post("/splits/calculate", json=request_data)
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_calculate_split_uses_cache(self):
        """Test calculate endpoint uses cache."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(splits_router)
        client = TestClient(app)

        with patch("src.routers.splits.get_api_key", return_value="test-key"):
            with patch("src.routers.splits.cache_service") as mock_cache:
                mock_cache.get_split_result = AsyncMock(return_value={"Alice": {"total": 25.0}})

                request_data = {
                    "person_names": ["Alice"],
                    "item_assignments": [],
                    "tax_amount_input": "0",
                    "tip_amount_input": "0",
                    "split_evenly": True,
                    "extracted_subtotal_from_gemini": 25.0,
                }

                client.post("/splits/calculate", json=request_data)
                # Should use cached result
                mock_cache.get_split_result.assert_called_once()


class TestViewSplitEndpoint:
    """Test view_split endpoint."""

    def test_view_split_endpoint_exists(self):
        """Test that view endpoint exists."""
        routes = [route.path for route in splits_router.routes]
        assert "/view/{split_id}" in routes

    @pytest.mark.asyncio
    async def test_view_split_success(self):
        """Test view split endpoint returns data."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(splits_router)
        client = TestClient(app)

        with patch("src.routers.splits.get_api_key", return_value="test-key"):
            response = client.get("/splits/view/abc123")
            assert response.status_code == 200
            data = response.json()
            assert "split_id" in data
            assert "calculated_split_results" in data

    @pytest.mark.asyncio
    async def test_view_split_uses_cache(self):
        """Test view split endpoint uses cache."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(splits_router)
        client = TestClient(app)

        with patch("src.routers.splits.get_api_key", return_value="test-key"):
            with patch("src.routers.splits.cache_service") as mock_cache:
                mock_cache.get_share_data = AsyncMock(return_value={"split_id": "abc123"})

                client.get("/splits/view/abc123")
                # Should use cached data
                mock_cache.get_share_data.assert_called_once()
