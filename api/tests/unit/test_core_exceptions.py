"""
Unit tests for core.exceptions module.
Tests custom exception hierarchy and HTTP status mapping.
"""


from src.core.exceptions import (
    SplitBillException,
    OCRProcessingError,
    ImageProcessingError,
    ValidationError,
    CacheError,
    StorageError,
    AuthenticationError,
    AuthorizationError,
    RateLimitExceededError,
    ConfigurationError,
    ExternalServiceError,
    EXCEPTION_HTTP_STATUS,
    get_http_status,
)


class TestSplitBillException:
    """Test base SplitBillException."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = SplitBillException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.details == {}

    def test_exception_with_details(self):
        """Test exception with details."""
        details = {"key": "value", "number": 123}
        exc = SplitBillException("Test error", details=details)
        assert exc.message == "Test error"
        assert exc.details == details

    def test_exception_to_dict(self):
        """Test exception to_dict method."""
        exc = SplitBillException("Test error", details={"key": "value"})
        result = exc.to_dict()
        assert "error" in result
        assert result["error"]["type"] == "SplitBillException"
        assert result["error"]["message"] == "Test error"
        assert result["error"]["details"] == {"key": "value"}

    def test_exception_to_dict_no_details(self):
        """Test exception to_dict without details."""
        exc = SplitBillException("Test error")
        result = exc.to_dict()
        assert result["error"]["details"] == {}


class TestOCRProcessingError:
    """Test OCRProcessingError."""

    def test_basic_ocr_error(self):
        """Test basic OCR error."""
        exc = OCRProcessingError("OCR failed")
        assert exc.message == "OCR failed"
        assert exc.error_type == "OCR_PROCESSING_FAILED"

    def test_ocr_error_with_details(self):
        """Test OCR error with custom details."""
        details = {"error_type": "CUSTOM_ERROR", "file": "test.jpg"}
        exc = OCRProcessingError("OCR failed", details=details)
        assert exc.error_type == "CUSTOM_ERROR"
        assert exc.details == details

    def test_ocr_error_without_error_type(self):
        """Test OCR error without error_type in details."""
        details = {"file": "test.jpg"}
        exc = OCRProcessingError("OCR failed", details=details)
        assert exc.error_type == "OCR_PROCESSING_FAILED"


class TestImageProcessingError:
    """Test ImageProcessingError."""

    def test_basic_image_error(self):
        """Test basic image error."""
        exc = ImageProcessingError("Invalid image format")
        assert exc.message == "Invalid image format"

    def test_image_error_with_details(self):
        """Test image error with details."""
        details = {"format": "unsupported", "file": "test.png"}
        exc = ImageProcessingError("Invalid image format", details=details)
        assert exc.details == details


class TestValidationError:
    """Test ValidationError."""

    def test_basic_validation_error(self):
        """Test basic validation error."""
        exc = ValidationError("Invalid input")
        assert exc.message == "Invalid input"
        assert exc.field is None

    def test_validation_error_with_field(self):
        """Test validation error with field."""
        exc = ValidationError("Invalid input", field="email")
        assert exc.field == "email"
        assert exc.details == {"field": "email"}

    def test_validation_error_with_details(self):
        """Test validation error with details."""
        details = {"constraint": "required", "value": None}
        exc = ValidationError("Invalid input", field="email", details=details)
        assert exc.field == "email"
        assert exc.details == {"field": "email", "constraint": "required", "value": None}


class TestCacheError:
    """Test CacheError."""

    def test_basic_cache_error(self):
        """Test basic cache error."""
        exc = CacheError("Cache operation failed")
        assert exc.message == "Cache operation failed"

    def test_cache_error_with_operation(self):
        """Test cache error with operation."""
        exc = CacheError("Cache operation failed", operation="get")
        assert exc.details == {"operation": "get"}

    def test_cache_error_with_key(self):
        """Test cache error with key."""
        exc = CacheError("Cache operation failed", key="test_key")
        assert exc.details == {"key": "test_key"}

    def test_cache_error_with_operation_and_key(self):
        """Test cache error with operation and key."""
        exc = CacheError("Cache operation failed", operation="set", key="test_key")
        assert exc.details == {"operation": "set", "key": "test_key"}


class TestStorageError:
    """Test StorageError."""

    def test_basic_storage_error(self):
        """Test basic storage error."""
        exc = StorageError("Storage operation failed")
        assert exc.message == "Storage operation failed"

    def test_storage_error_with_operation(self):
        """Test storage error with operation."""
        exc = StorageError("Storage operation failed", operation="upload")
        assert exc.details == {"operation": "upload"}

    def test_storage_error_with_bucket(self):
        """Test storage error with bucket."""
        exc = StorageError("Storage operation failed", bucket="test-bucket")
        assert exc.details == {"bucket": "test-bucket"}

    def test_storage_error_with_operation_and_bucket(self):
        """Test storage error with operation and bucket."""
        exc = StorageError("Storage operation failed", operation="download", bucket="test-bucket")
        assert exc.details == {"operation": "download", "bucket": "test-bucket"}


class TestAuthenticationError:
    """Test AuthenticationError."""

    def test_basic_auth_error(self):
        """Test basic authentication error."""
        exc = AuthenticationError()
        assert exc.message == "Authentication failed"

    def test_custom_auth_error(self):
        """Test custom authentication error."""
        exc = AuthenticationError("Invalid credentials")
        assert exc.message == "Invalid credentials"


class TestAuthorizationError:
    """Test AuthorizationError."""

    def test_basic_authz_error(self):
        """Test basic authorization error."""
        exc = AuthorizationError()
        assert exc.message == "Access denied"

    def test_custom_authz_error(self):
        """Test custom authorization error."""
        exc = AuthorizationError("Permission denied")
        assert exc.message == "Permission denied"

    def test_authz_error_with_details(self):
        """Test authorization error with details."""
        details = {"resource": "admin", "action": "delete"}
        exc = AuthorizationError("Permission denied", details=details)
        assert exc.details == details


class TestRateLimitExceededError:
    """Test RateLimitExceededError."""

    def test_basic_rate_limit_error(self):
        """Test basic rate limit error."""
        exc = RateLimitExceededError()
        assert exc.message == "Rate limit exceeded"

    def test_rate_limit_with_limit(self):
        """Test rate limit error with limit."""
        exc = RateLimitExceededError(limit=100)
        assert exc.details == {"limit": 100}

    def test_rate_limit_with_window(self):
        """Test rate limit error with window."""
        exc = RateLimitExceededError(window=60)
        assert exc.details == {"window_seconds": 60}

    def test_rate_limit_with_retry_after(self):
        """Test rate limit error with retry_after."""
        exc = RateLimitExceededError(retry_after=30)
        assert exc.details == {"retry_after_seconds": 30}

    def test_rate_limit_with_all_params(self):
        """Test rate limit error with all parameters."""
        exc = RateLimitExceededError(limit=100, window=60, retry_after=30)
        assert exc.details == {
            "limit": 100,
            "window_seconds": 60,
            "retry_after_seconds": 30,
        }


class TestConfigurationError:
    """Test ConfigurationError."""

    def test_basic_config_error(self):
        """Test basic configuration error."""
        exc = ConfigurationError("Invalid configuration")
        assert exc.message == "Invalid configuration"

    def test_config_error_with_key(self):
        """Test configuration error with config key."""
        exc = ConfigurationError("Invalid configuration", config_key="API_KEY")
        assert exc.details == {"config_key": "API_KEY"}


class TestExternalServiceError:
    """Test ExternalServiceError."""

    def test_basic_external_error(self):
        """Test basic external service error."""
        exc = ExternalServiceError("Service unavailable")
        assert exc.message == "Service unavailable"

    def test_external_error_with_service_name(self):
        """Test external service error with service name."""
        exc = ExternalServiceError("Service unavailable", service_name="OpenRouter")
        assert exc.details == {"service": "OpenRouter"}

    def test_external_error_with_status_code(self):
        """Test external service error with status code."""
        exc = ExternalServiceError("Service error", status_code=500)
        assert exc.details == {"status_code": 500}

    def test_external_error_with_response_body(self):
        """Test external service error with response body."""
        body = "Error details from service"
        exc = ExternalServiceError("Service error", response_body=body)
        assert exc.details == {"response_body": body}

    def test_external_error_with_long_response_body(self):
        """Test external service error truncates long response body."""
        long_body = "x" * 600  # Longer than 500 characters
        exc = ExternalServiceError("Service error", response_body=long_body)
        assert len(exc.details["response_body"]) == 500
        assert exc.details["response_body"].endswith("...")

    def test_external_error_with_all_params(self):
        """Test external service error with all parameters."""
        exc = ExternalServiceError(
            "Service error",
            service_name="OpenRouter",
            status_code=500,
            response_body="Error details",
        )
        assert exc.details == {
            "service": "OpenRouter",
            "status_code": 500,
            "response_body": "Error details",
        }


class TestExceptionHTTPStatusMapping:
    """Test exception to HTTP status code mapping."""

    def test_split_bill_exception_status(self):
        """Test SplitBillException status code."""
        exc = SplitBillException("Test error")
        status = get_http_status(exc)
        assert status == 500

    def test_ocr_processing_error_status(self):
        """Test OCRProcessingError status code."""
        exc = OCRProcessingError("OCR failed")
        status = get_http_status(exc)
        assert status == 400

    def test_image_processing_error_status(self):
        """Test ImageProcessingError status code."""
        exc = ImageProcessingError("Invalid image")
        status = get_http_status(exc)
        assert status == 400

    def test_validation_error_status(self):
        """Test ValidationError status code."""
        exc = ValidationError("Invalid input")
        status = get_http_status(exc)
        assert status == 422

    def test_cache_error_status(self):
        """Test CacheError status code."""
        exc = CacheError("Cache failed")
        status = get_http_status(exc)
        assert status == 503

    def test_storage_error_status(self):
        """Test StorageError status code."""
        exc = StorageError("Storage failed")
        status = get_http_status(exc)
        assert status == 503

    def test_authentication_error_status(self):
        """Test AuthenticationError status code."""
        exc = AuthenticationError()
        status = get_http_status(exc)
        assert status == 401

    def test_authorization_error_status(self):
        """Test AuthorizationError status code."""
        exc = AuthorizationError()
        status = get_http_status(exc)
        assert status == 403

    def test_rate_limit_exceeded_error_status(self):
        """Test RateLimitExceededError status code."""
        exc = RateLimitExceededError()
        status = get_http_status(exc)
        assert status == 429

    def test_configuration_error_status(self):
        """Test ConfigurationError status code."""
        exc = ConfigurationError("Invalid config")
        status = get_http_status(exc)
        assert status == 500

    def test_external_service_error_status(self):
        """Test ExternalServiceError status code."""
        exc = ExternalServiceError("Service error")
        status = get_http_status(exc)
        assert status == 502


class TestExceptionInheritance:
    """Test exception inheritance."""

    def test_all_exceptions_inherit_from_base(self):
        """Test all custom exceptions inherit from SplitBillException."""
        exceptions = [
            OCRProcessingError("test"),
            ImageProcessingError("test"),
            ValidationError("test"),
            CacheError("test"),
            StorageError("test"),
            AuthenticationError(),
            AuthorizationError(),
            RateLimitExceededError(),
            ConfigurationError("test"),
            ExternalServiceError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, SplitBillException)

    def test_rate_limit_inherits_from_authorization(self):
        """Test RateLimitExceededError inherits from AuthorizationError."""
        exc = RateLimitExceededError()
        assert isinstance(exc, AuthorizationError)
        assert isinstance(exc, SplitBillException)


class TestExceptionHTTPStatusMappingDictionary:
    """Test EXCEPTION_HTTP_STATUS mapping dictionary."""

    def test_mapping_exists(self):
        """Test that EXCEPTION_HTTP_STATUS mapping exists."""
        assert isinstance(EXCEPTION_HTTP_STATUS, dict)
        assert len(EXCEPTION_HTTP_STATUS) > 0

    def test_mapping_contains_all_exceptions(self):
        """Test mapping contains all exception types."""
        exception_types = [
            SplitBillException,
            OCRProcessingError,
            ImageProcessingError,
            ValidationError,
            CacheError,
            StorageError,
            AuthenticationError,
            AuthorizationError,
            RateLimitExceededError,
            ConfigurationError,
            ExternalServiceError,
        ]

        for exc_type in exception_types:
            assert exc_type in EXCEPTION_HTTP_STATUS

    def test_mapping_status_codes_are_valid(self):
        """Test all status codes are valid HTTP status codes."""
        valid_status_codes = {200, 201, 204, 400, 401, 403, 404, 422, 429, 500, 502, 503}

        for exc_type, status_code in EXCEPTION_HTTP_STATUS.items():
            assert status_code in valid_status_codes
