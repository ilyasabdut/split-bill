"""
Unit tests for core.logging_config module.
Tests structured logging with correlation context.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.core.logging_config import (
    CorrelationIdMiddleware,
    LoggingContextFilter,
    setup_standard_logging,
    get_logger,
    log_request,
    log_error,
    log_performance,
    log_security_event,
    performance_monitor,
    request_monitor,
    LoggingConfig,
    correlation_id,
)


class TestCorrelationIdMiddleware:
    """Test CorrelationIdMiddleware."""

    @pytest.mark.asyncio
    async def test_generates_correlation_id(self):
        """Test middleware generates correlation ID."""
        middleware = CorrelationIdMiddleware()
        mock_request = MagicMock()
        mock_request.headers = MagicMock(get=lambda x: None)
        mock_request.state = MagicMock()

        async def call_next(request):
            return MagicMock(headers={})

        response = await middleware.dispatch(mock_request, call_next)
        assert "X-Correlation-ID" in response.headers

    @pytest.mark.asyncio
    async def test_uses_existing_correlation_id(self):
        """Test middleware uses existing correlation ID from header."""
        middleware = CorrelationIdMiddleware()
        mock_request = MagicMock()
        mock_request.headers = MagicMock(get=lambda x: "existing-correlation-id" if x == "X-Correlation-ID" else None)
        mock_request.state = MagicMock()

        async def call_next(request):
            return MagicMock(headers={})

        response = await middleware.dispatch(mock_request, call_next)
        assert response.headers["X-Correlation-ID"] == "existing-correlation-id"

    @pytest.mark.asyncio
    async def test_sets_correlation_id_in_state(self):
        """Test middleware sets correlation ID in request state."""
        middleware = CorrelationIdMiddleware()
        mock_request = MagicMock()
        mock_request.headers = MagicMock(get=lambda x: None)
        mock_request.state = MagicMock()

        async def call_next(request):
            return MagicMock(headers={})

        await middleware.dispatch(mock_request, call_next)
        assert hasattr(mock_request.state, "correlation_id")


class TestLoggingContextFilter:
    """Test LoggingContextFilter."""

    def test_filter_adds_correlation_id(self):
        """Test filter adds correlation ID to log record."""
        filter_instance = LoggingContextFilter()
        record = MagicMock()

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            result = filter_instance.filter(record)
            assert result is True
            assert hasattr(record, "correlation_id")
            assert record.correlation_id == "test-correlation-id"

    def test_filter_no_correlation_id(self):
        """Test filter when no correlation ID is set."""
        filter_instance = LoggingContextFilter()
        record = MagicMock()

        with patch.object(correlation_id, "get", return_value=""):
            result = filter_instance.filter(record)
            assert result is True
            assert record.correlation_id == "no-correlation-id"


class TestSetupStandardLogging:
    """Test setup_standard_logging."""

    @patch("src.core.logging_config.logging")
    def test_setup_standard_logging(self, mock_logging):
        """Test setup_standard_logging configures logging."""
        result = setup_standard_logging()
        assert mock_logging.basicConfig.basicConfig.called
        assert result is not None


class TestGetLogger:
    """Test get_logger function."""

    @patch("src.core.logging_config.logging")
    def test_get_logger_with_name(self, mock_logging):
        """Test get_logger with name."""
        get_logger("test_module")
        mock_logging.getLogger.assert_called_with("test_module")

    @patch("src.core.logging_config.logging")
    def test_get_logger_default_name(self, mock_logging):
        """Test get_logger with default name."""
        get_logger()
        mock_logging.getLogger.assert_called()


class TestLogRequest:
    """Test log_request function."""

    def test_log_request(self):
        """Test log_request logs request details."""
        mock_logger = MagicMock()
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = MagicMock(path="/api/test")
        mock_request.headers = MagicMock(get=lambda x: "test-agent" if x == "user-agent" else None)
        mock_request.client = MagicMock(host="127.0.0.1")
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            log_request(mock_logger, mock_request, mock_response, 123.45)
            mock_logger.info.assert_called()

    def test_log_request_without_client(self):
        """Test log_request handles request without client."""
        mock_logger = MagicMock()
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url = MagicMock(path="/api/test")
        mock_request.headers = MagicMock(get=lambda x: "test-agent" if x == "user-agent" else None)
        mock_request.client = None
        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            log_request(mock_logger, mock_request, mock_response, 456.78)
            mock_logger.info.assert_called()


class TestLogError:
    """Test log_error function."""

    def test_log_error(self):
        """Test log_error logs error with context."""
        mock_logger = MagicMock()
        error = ValueError("Test error")

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            log_error(mock_logger, error)
            mock_logger.error.assert_called()

    def test_log_error_with_context(self):
        """Test log_error with additional context."""
        mock_logger = MagicMock()
        error = RuntimeError("Test error")
        context = {"user_id": "123", "action": "test"}

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            log_error(mock_logger, error, context)
            mock_logger.error.assert_called()


class TestLogPerformance:
    """Test log_performance function."""

    def test_log_performance(self):
        """Test log_performance logs performance metrics."""
        mock_logger = MagicMock()

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            log_performance(mock_logger, "test_operation", 123.45)
            mock_logger.info.assert_called()

    def test_log_performance_with_context(self):
        """Test log_performance with additional context."""
        mock_logger = MagicMock()
        context = {"user_id": "123", "endpoint": "/api/test"}

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            log_performance(mock_logger, "test_operation", 123.45, context)
            mock_logger.info.assert_called()


class TestLogSecurityEvent:
    """Test log_security_event function."""

    def test_log_security_event(self):
        """Test log_security_event logs security events."""
        mock_logger = MagicMock()

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            log_security_event(mock_logger, "test_event")
            mock_logger.warning.assert_called()

    def test_log_security_event_with_details(self):
        """Test log_security_event with details."""
        mock_logger = MagicMock()
        details = {"user_id": "123", "ip": "127.0.0.1"}

        with patch.object(correlation_id, "get", return_value="test-correlation-id"):
            log_security_event(mock_logger, "test_event", details)
            mock_logger.warning.assert_called()


class TestPerformanceMonitor:
    """Test performance_monitor decorator."""

    @pytest.mark.asyncio
    async def test_performance_monitor_success(self):
        """Test performance_monitor logs successful operations."""
        @performance_monitor("test_operation")
        async def test_func():
            return "result"

        with patch("src.core.logging_config.logger") as mock_logger:
            result = await test_func()
            assert result == "result"
            assert mock_logger.info.called

    @pytest.mark.asyncio
    async def test_performance_monitor_error(self):
        """Test performance_monitor logs failed operations."""
        @performance_monitor("test_operation")
        async def test_func():
            raise ValueError("Test error")

        with patch("src.core.logging_config.logger") as mock_logger:
            with pytest.raises(ValueError):
                await test_func()
            assert mock_logger.error.called


class TestRequestMonitor:
    """Test request_monitor decorator."""

    @pytest.mark.asyncio
    async def test_request_monitor_success(self):
        """Test request_monitor logs successful requests."""
        @request_monitor("test_endpoint")
        async def test_func():
            return "result"

        with patch("src.core.logging_config.logger"):
            result = await test_func()
            assert result == "result"

    @pytest.mark.asyncio
    async def test_request_monitor_error(self):
        """Test request_monitor logs failed requests."""
        @request_monitor("test_endpoint")
        async def test_func():
            raise ValueError("Test error")

        with patch("src.core.logging_config.logger"):
            with pytest.raises(ValueError):
                await test_func()


class TestLoggingConfig:
    """Test LoggingConfig class."""

    def test_logging_config_initialization(self):
        """Test LoggingConfig initialization."""
        config = LoggingConfig()
        assert config.correlation_id_header == "X-Correlation-ID"
        assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert config.enable_performance_logging is True
        assert config.enable_security_logging is True


class TestCorrelationIdContextVar:
    """Test correlation_id context variable."""

    def test_correlation_id_context_var_exists(self):
        """Test that correlation_id context variable exists."""
        assert correlation_id is not None

    def test_correlation_id_default_value(self):
        """Test correlation_id default value."""
        assert correlation_id.get() == ""
