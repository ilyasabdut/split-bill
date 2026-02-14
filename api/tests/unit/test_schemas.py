"""Tests for schemas module."""

from datetime import datetime
from typing import Any, Dict, List

import pytest
from pydantic import ValidationError

from src.models.schemas import (
    LineItem,
    Discount,
    TaxDetail,
    ReceiptData,
    ReceiptUploadResponse,
    ItemAssignment,
    PaymentDetails,
    CalculateSplitRequest,
    CalculateSplitResponse,
    SharedSplitDataResponse,
    ErrorResponse,
    HealthStatus,
    ComponentHealth,
    DetailedHealthResponse,
    LogEntry,
    MetricData,
    PaginationParams,
    PaginationResponse,
    ApiResponse,
)


class TestLineItem:
    """Tests for LineItem schema."""

    def test_valid_line_item(self):
        """Test creating a valid line item."""
        item = LineItem(
            item_description="Test Item",
            quantity=2.0,
            item_total_price=10.0
        )
        assert item.item_description == "Test Item"
        assert item.quantity == 2.0
        assert item.item_total_price == 10.0

    def test_default_quantity(self):
        """Test that quantity defaults to 1.0."""
        item = LineItem(
            item_description="Test Item",
            item_total_price=5.0
        )
        assert item.quantity == 1.0

    def test_description_required(self):
        """Test that description is required."""
        with pytest.raises(ValidationError):
            LineItem(quantity=1.0, item_total_price=5.0)


class TestDiscount:
    """Tests for Discount schema."""

    def test_valid_discount(self):
        """Test creating a valid discount."""
        discount = Discount(description="10% off", amount=5.0)
        assert discount.description == "10% off"
        assert discount.amount == 5.0


class TestTaxDetail:
    """Tests for TaxDetail schema."""

    def test_valid_tax_detail(self):
        """Test creating a valid tax detail."""
        tax = TaxDetail(tax_label="VAT 10%", tax_amount=1.5)
        assert tax.tax_label == "VAT 10%"
        assert tax.tax_amount == 1.5


class TestReceiptData:
    """Tests for ReceiptData schema."""

    def test_valid_receipt_data(self):
        """Test creating valid receipt data."""
        receipt = ReceiptData(
            store_name="Test Store",
            transaction_date="2024-01-15",
            line_items=[
                LineItem(item_description="Item 1", item_total_price=10.0),
                LineItem(item_description="Item 2", item_total_price=20.0),
            ],
            subtotal=30.0,
            total_amount=33.0,
        )
        assert receipt.store_name == "Test Store"
        assert len(receipt.line_items) == 2
        assert receipt.subtotal == 30.0

    def test_optional_fields(self):
        """Test that optional fields can be None."""
        receipt = ReceiptData()
        assert receipt.store_name is None
        assert receipt.total_amount is None
        assert receipt.line_items == []

    def test_default_empty_lists(self):
        """Test that list fields default to empty lists."""
        receipt = ReceiptData()
        assert receipt.line_items == []
        assert receipt.discounts == []
        assert receipt.tax_details == []


class TestReceiptUploadResponse:
    """Tests for ReceiptUploadResponse schema."""

    def test_valid_response(self):
        """Test creating valid upload response."""
        response = ReceiptUploadResponse(
            parsed_data={"items": []},
            extracted_subtotal_from_gemini=50.0,
            extracted_total_discount=0.0,
        )
        assert response.extracted_subtotal_from_gemini == 50.0
        assert response.minio_image_object_name is None


class TestItemAssignment:
    """Tests for ItemAssignment schema."""

    def test_valid_assignment(self):
        """Test creating valid item assignment."""
        assignment = ItemAssignment(
            item_details={"name": "Pizza", "price": 25.0},
            assigned_to=["Alice", "Bob"]
        )
        assert assignment.assigned_to == ["Alice", "Bob"]


class TestPaymentDetails:
    """Tests for PaymentDetails schema."""

    def test_valid_payment_details(self):
        """Test creating valid payment details."""
        payment = PaymentDetails(
            method="Bank",
            bank_name="Test Bank",
            account_id="1234567890",
            account_holder="John Doe"
        )
        assert payment.method == "Bank"
        assert payment.bank_name == "Test Bank"

    def test_optional_fields_bank(self):
        """Test that bank fields are optional."""
        payment = PaymentDetails(method="Cash")
        assert payment.bank_name is None
        assert payment.account_id is None

    def test_e_wallet_fields(self):
        """Test e-wallet payment details."""
        payment = PaymentDetails(
            method="E-Wallet",
            e_wallet_provider="GoPay"
        )
        assert payment.e_wallet_provider == "GoPay"


class TestCalculateSplitRequest:
    """Tests for CalculateSplitRequest schema."""

    def test_valid_request(self):
        """Test creating valid split request."""
        request = CalculateSplitRequest(
            person_names=["Alice", "Bob"],
            item_assignments=[
                ItemAssignment(
                    item_details={"name": "Pizza", "price": 25.0},
                    assigned_to=["Alice"]
                )
            ],
            tax_amount_input=2.5,
            tip_amount_input=5.0,
            split_evenly=False,
            extracted_total_discount=0.0,
            original_parsed_data={}
        )
        assert len(request.person_names) == 2
        assert request.split_evenly is False


class TestCalculateSplitResponse:
    """Tests for CalculateSplitResponse schema."""

    def test_valid_response(self):
        """Test creating valid split response."""
        response = CalculateSplitResponse(
            split_results={"Alice": {"total": 15.0}},
            share_link="http://example.com/split/123",
            split_id="split-123"
        )
        assert response.split_id == "split-123"
        assert response.share_link == "http://example.com/split/123"


class TestSharedSplitDataResponse:
    """Tests for SharedSplitDataResponse schema."""

    def test_valid_response(self):
        """Test creating valid shared split response."""
        response = SharedSplitDataResponse(
            split_id="split-123",
            original_parsed_data={},
            person_names=["Alice", "Bob"],
            item_assignments=[],
            split_evenly_choice=False,
            total_discount_applied=0.0,
            user_adjusted_tax=0.0,
            user_adjusted_tip=0.0,
            calculated_split_results={},
            share_link="http://example.com/split/123",
            creation_timestamp=1640995200.0,
            notes_text=""
        )
        assert response.split_id == "split-123"
        assert response.creation_timestamp == 1640995200.0


class TestErrorResponse:
    """Tests for ErrorResponse schema."""

    def test_valid_error(self):
        """Test creating valid error response."""
        error = ErrorResponse(
            error="ValidationError",
            message="Invalid input data",
            details={"field": "price", "error": "must be positive"}
        )
        assert error.error == "ValidationError"
        assert error.message == "Invalid input data"
        assert error.details["field"] == "price"

    def test_optional_details(self):
        """Test that details field is optional."""
        error = ErrorResponse(error="NotFound", message="Item not found")
        assert error.details is None


class TestHealthStatus:
    """Tests for HealthStatus schema."""

    def test_valid_status(self):
        """Test creating valid health status."""
        status = HealthStatus(status="healthy", version="2.0.0")
        assert status.status == "healthy"
        assert status.version == "2.0.0"
        assert isinstance(status.timestamp, datetime)

    def test_default_version(self):
        """Test that version has default value."""
        status = HealthStatus(status="healthy")
        assert status.version == "1.0.0"


class TestComponentHealth:
    """Tests for ComponentHealth schema."""

    def test_valid_component(self):
        """Test creating valid component health."""
        component = ComponentHealth(
            name="database",
            status="healthy",
            message="Connection established",
            response_time=0.05
        )
        assert component.name == "database"
        assert component.status == "healthy"
        assert component.response_time == 0.05


class TestDetailedHealthResponse:
    """Tests for DetailedHealthResponse schema."""

    def test_valid_response(self):
        """Test creating valid detailed health response."""
        response = DetailedHealthResponse(
            overall_status=HealthStatus(status="healthy"),
            components=[
                ComponentHealth(name="db", status="healthy"),
                ComponentHealth(name="cache", status="healthy"),
            ],
            uptime_seconds=86400.0
        )
        assert response.uptime_seconds == 86400.0
        assert len(response.components) == 2


class TestLogEntry:
    """Tests for LogEntry schema."""

    def test_valid_log_entry(self):
        """Test creating valid log entry."""
        entry = LogEntry(
            level="INFO",
            message="Application started",
            module="main",
            function="startup",
            line_number=42,
            extra_data={"user_id": "123"}
        )
        assert entry.level == "INFO"
        assert entry.message == "Application started"
        assert entry.function == "startup"

    def test_default_timestamp(self):
        """Test that timestamp defaults to current time."""
        entry = LogEntry(level="DEBUG", message="Test", module="test")
        assert isinstance(entry.timestamp, datetime)

    def test_optional_fields(self):
        """Test that optional fields can be None."""
        entry = LogEntry(level="ERROR", message="Error occurred", module="error")
        assert entry.function is None
        assert entry.line_number is None
        assert entry.extra_data is None


class TestMetricData:
    """Tests for MetricData schema."""

    def test_valid_metric(self):
        """Test creating valid metric."""
        metric = MetricData(
            name="request_count",
            value=100.0,
            labels={"endpoint": "/api/split"}
        )
        assert metric.name == "request_count"
        assert metric.value == 100.0
        assert metric.labels["endpoint"] == "/api/split"

    def test_default_timestamp(self):
        """Test that timestamp defaults to current time."""
        metric = MetricData(name="test", value=1.0)
        assert isinstance(metric.timestamp, datetime)

    def test_optional_labels(self):
        """Test that labels field is optional."""
        metric = MetricData(name="test", value=1.0)
        assert metric.labels is None


class TestPaginationParams:
    """Tests for PaginationParams schema."""

    def test_valid_params(self):
        """Test creating valid pagination params."""
        params = PaginationParams(page=2, size=50)
        assert params.page == 2
        assert params.size == 50

    def test_default_values(self):
        """Test that default values are set correctly."""
        params = PaginationParams()
        assert params.page == 1
        assert params.size == 20

    def test_page_minimum(self):
        """Test that page must be at least 1."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_size_range(self):
        """Test that size has valid range."""
        with pytest.raises(ValidationError):
            PaginationParams(size=0)
        with pytest.raises(ValidationError):
            PaginationParams(size=101)


class TestPaginationResponse:
    """Tests for PaginationResponse schema."""

    def test_valid_response(self):
        """Test creating valid pagination response."""
        response = PaginationResponse(
            items=[{"id": 1}, {"id": 2}],
            total=100,
            page=1,
            size=20,
            pages=5
        )
        assert response.total == 100
        assert response.pages == 5


class TestApiResponse:
    """Tests for ApiResponse schema."""

    def test_successful_response(self):
        """Test creating successful API response."""
        response = ApiResponse(
            success=True,
            message="Operation completed",
            data={"id": "123"}
        )
        assert response.success is True
        assert response.message == "Operation completed"
        assert response.data["id"] == "123"
        assert response.error is None

    def test_error_response(self):
        """Test creating error API response."""
        error = ErrorResponse(error="ValidationError", message="Invalid input")
        response = ApiResponse(
            success=False,
            message="Request failed",
            error=error
        )
        assert response.success is False
        assert response.error is not None
        assert response.error.error == "ValidationError"

    def test_default_success(self):
        """Test that success defaults to True."""
        response = ApiResponse(data={"test": "data"})
        assert response.success is True

    def test_default_timestamp(self):
        """Test that timestamp defaults to current time."""
        response = ApiResponse()
        assert isinstance(response.timestamp, datetime)
