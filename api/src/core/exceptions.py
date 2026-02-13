"""Custom exception hierarchy for the Split Bill application.

This module defines a structured exception hierarchy to provide clear,
actionable error messages across the application.
"""

from typing import Any, Dict, Optional


class SplitBillException(Exception):
    """Base exception for the Split Bill application.

    All custom exceptions inherit from this class, providing a consistent
    interface for error handling across the application.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "type": self.__class__.__name__,
                "message": self.message,
                "details": self.details,
            }
        }


class OCRProcessingError(SplitBillException):
    """Raised when OCR processing fails.

    This exception is raised when:
    - The image cannot be processed by the OCR service
    - The OCR service returns an invalid response
    - Image classification fails (not a receipt)
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.error_type = (
            details.get("error_type", "OCR_PROCESSING_FAILED")
            if details
            else "OCR_PROCESSING_FAILED"
        )


class ImageProcessingError(SplitBillException):
    """Raised when image processing fails.

    This exception is raised when:
    - The image format is invalid or unsupported
    - Image compression fails
    - Image validation fails
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ValidationError(SplitBillException):
    """Raised when input validation fails.

    This exception is raised when:
    - Request validation fails (Pydantic)
    - Business rule validation fails
    - Input constraints are violated
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.field = field
        error_details = {"field": field} if field else {}
        if details:
            error_details.update(details)
        super().__init__(message, error_details)


class CacheError(SplitBillException):
    """Raised when a cache operation fails.

    This exception is raised when:
    - Redis connection fails
    - Cache read/write operations fail
    - Cache key operations fail (get, set, delete)
    """

    def __init__(
        self, message: str, operation: Optional[str] = None, key: Optional[str] = None
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if key:
            details["key"] = key
        super().__init__(message, details)


class StorageError(SplitBillException):
    """Raised when storage operations fail.

    This exception is raised when:
    - MinIO/S3 operations fail
    - File upload/download fails
    - Bucket access fails
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        bucket: Optional[str] = None,
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if bucket:
            details["bucket"] = bucket
        super().__init__(message, details)


class AuthenticationError(SplitBillException):
    """Raised when authentication fails.

    This exception is raised when:
    - API key validation fails
    - Token validation fails
    - Authentication credentials are missing
    """

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class AuthorizationError(SplitBillException):
    """Raised when authorization fails.

    This exception is raised when:
    - User is not authorized to perform an action
    - Rate limit is exceeded
    - Access to resource is denied
    """

    def __init__(
        self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)


class RateLimitExceededError(AuthorizationError):
    """Raised when rate limit is exceeded.

    This exception is raised when:
    - Client exceeds configured rate limits
    - Request throttling is triggered
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[int] = None,
        retry_after: Optional[int] = None,
    ):
        details = {}
        if limit:
            details["limit"] = limit
        if window:
            details["window_seconds"] = window
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(message, details)


class ConfigurationError(SplitBillException):
    """Raised when configuration is invalid or missing.

    This exception is raised when:
    - Required environment variables are missing
    - Configuration values are invalid
    - Service configuration fails
    """

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details)


class ExternalServiceError(SplitBillException):
    """Raised when an external service call fails.

    This exception is raised when:
    - Third-party API calls fail
    - External service is unavailable
    - Network errors occur
    """

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        details = {}
        if service_name:
            details["service"] = service_name
        if status_code:
            details["status_code"] = status_code
        if response_body:
            details["response_body"] = response_body[:500]  # Truncate long responses
        super().__init__(message, details)


# Exception-to-HTTP status code mapping
EXCEPTION_HTTP_STATUS = {
    SplitBillException: 500,
    OCRProcessingError: 400,
    ImageProcessingError: 400,
    ValidationError: 422,
    CacheError: 503,
    StorageError: 503,
    AuthenticationError: 401,
    AuthorizationError: 403,
    RateLimitExceededError: 429,
    ConfigurationError: 500,
    ExternalServiceError: 502,
}


def get_http_status(exception: SplitBillException) -> int:
    """Get the appropriate HTTP status code for an exception.

    Args:
        exception: A SplitBillException instance

    Returns:
        HTTP status code integer
    """
    for exc_type, status in EXCEPTION_HTTP_STATUS.items():
        if isinstance(exception, exc_type):
            return status
    return 500
