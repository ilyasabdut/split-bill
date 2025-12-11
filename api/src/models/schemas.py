"""
Pydantic models for request/response schemas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# OCR and Receipt Models
class LineItem(BaseModel):
    """Schema for a line item extracted from receipt."""

    item_description: str = Field(..., description="Full description of the item")
    quantity: float = Field(default=1.0, description="Quantity of the item")
    item_total_price: float = Field(..., description="Total price for the item line")


class Discount(BaseModel):
    """Schema for a discount applied to receipt."""

    description: str = Field(..., description="Description of the discount")
    amount: float = Field(..., description="Positive numeric value of the discount")


class TaxDetail(BaseModel):
    """Schema for tax details on receipt."""

    tax_label: str = Field(..., description="Label for the tax or charge")
    tax_amount: float = Field(..., description="Amount of the tax or charge")


class ReceiptData(BaseModel):
    """Schema for extracted receipt data."""

    store_name: Optional[str] = Field(default=None, description="Name of the store")
    transaction_date: Optional[str] = Field(
        default=None, description="Transaction date (YYYY-MM-DD)"
    )
    transaction_time: Optional[str] = Field(
        default=None, description="Transaction time (HH:MM)"
    )
    line_items: List[LineItem] = Field(default_factory=list)
    discounts: List[Discount] = Field(default_factory=list)
    tax_details: List[TaxDetail] = Field(default_factory=list)
    subtotal: Optional[float] = Field(
        default=None, description="Subtotal before taxes/discounts"
    )
    total_amount: Optional[float] = Field(
        default=None, description="The final grand total paid"
    )
    tip_amount: Optional[float] = Field(
        default=None, description="Tip or gratuity amount"
    )


# API Request Models
class ReceiptUploadResponse(BaseModel):
    """Schema for receipt upload response."""

    parsed_data: Dict[str, Any]
    processed_image_bytes_base64: Optional[str] = Field(
        default=None, description="Base64 encoded image for display"
    )
    minio_image_object_name: Optional[str] = Field(default=None)
    extracted_subtotal_from_gemini: float
    extracted_total_discount: float


class ItemAssignment(BaseModel):
    """Schema for item assignment to people."""

    item_details: Dict[str, Any]
    assigned_to: List[str]


class PaymentDetails(BaseModel):
    """Schema for payment details."""

    method: str = Field(..., description="Payment method (Cash, Bank, E-Wallet, Other)")
    bank_name: Optional[str] = Field(
        default=None, description="Bank name for bank payments"
    )
    account_id: Optional[str] = Field(default=None, description="Account number or ID")
    account_holder: Optional[str] = Field(
        default=None, description="Account holder name"
    )
    e_wallet_provider: Optional[str] = Field(
        default=None, description="E-wallet provider"
    )


class CalculateSplitRequest(BaseModel):
    """Schema for split calculation request."""

    person_names: List[str]
    item_assignments: List[ItemAssignment]
    tax_amount_input: float
    tip_amount_input: float
    split_evenly: bool
    extracted_subtotal_from_gemini: Optional[float] = Field(default=None)
    extracted_total_discount: float
    processed_image_bytes_for_minio_base64: Optional[str] = Field(
        default=None, description="Base64 encoded image for MinIO upload"
    )
    original_parsed_data: Dict[str, Any]
    notes_text: Optional[str] = Field(default=None)
    payment_details: Optional[PaymentDetails] = Field(default=None)


# API Response Models
class CalculateSplitResponse(BaseModel):
    """Schema for split calculation response."""

    split_results: Dict[str, Any]
    share_link: str
    split_id: str


class SharedSplitDataResponse(BaseModel):
    """Schema for shared split data response."""

    split_id: str
    original_parsed_data: Dict[str, Any]
    person_names: List[str]
    item_assignments: List[ItemAssignment]
    split_evenly_choice: bool
    total_discount_applied: float
    user_adjusted_tax: float
    user_adjusted_tip: float
    calculated_split_results: Dict[str, Any]
    minio_image_object_name: Optional[str]
    share_link: str
    creation_timestamp: float
    image_bytes_for_display_base64: Optional[str] = Field(
        default=None, description="Base64 encoded image for display"
    )
    notes_text: str
    payment_details: Dict[str, Any] = Field(default_factory=dict)


# Error Models
class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )


# Health Check Models
class HealthStatus(BaseModel):
    """Schema for health check status."""

    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Check timestamp"
    )
    version: str = Field(default="1.0.0", description="Application version")


class ComponentHealth(BaseModel):
    """Schema for individual component health."""

    name: str = Field(..., description="Component name")
    status: str = Field(
        ..., description="Component status (healthy, degraded, unhealthy)"
    )
    message: Optional[str] = Field(default=None, description="Status message")
    response_time: Optional[float] = Field(
        default=None, description="Response time in seconds"
    )


class DetailedHealthResponse(BaseModel):
    """Schema for detailed health check response."""

    overall_status: HealthStatus
    components: List[ComponentHealth]
    uptime_seconds: float = Field(..., description="Application uptime in seconds")


# Logging and Monitoring Models
class LogEntry(BaseModel):
    """Schema for structured log entries."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(
        ..., description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    message: str = Field(..., description="Log message")
    module: str = Field(..., description="Module name")
    function: Optional[str] = Field(default=None, description="Function name")
    line_number: Optional[int] = Field(default=None, description="Line number")
    extra_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional structured data"
    )


class MetricData(BaseModel):
    """Schema for application metrics."""

    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    labels: Optional[Dict[str, str]] = Field(
        default=None, description="Metric labels/tags"
    )


# Utility Models
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginationResponse(BaseModel):
    """Schema for paginated response."""

    items: List[Any]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class ApiResponse(BaseModel):
    """Generic API response wrapper."""

    success: bool = Field(
        default=True, description="Whether the request was successful"
    )
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[ErrorResponse] = Field(
        default=None, description="Error information if any"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
