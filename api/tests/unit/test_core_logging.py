"""
Unit tests for core.logging module.
Tests logging configuration and middleware.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.core.logging import (
setup_logging,
get_logger,
LoggingContextFilter,
log_request_middleware,
)


class TestSetupLogging:
    """Test logging setup functionality."""

    @patch("src.core.logging.logger")
    def test_setup_logging_default_params(self, mock_logger):
        """Test setup_logging with default parameters."""
        setup_logging()
        mock_logger.remove.assert_called_once()
        assert mock_logger.add.call_count >= 2  # Console and file handlers

    @patch("src.core.logging.logger")
    def test_setup_logging_custom_level(self, mock_logger):
        """Test setup_logging with custom log level."""
        setup_logging(log_level="DEBUG")
        # Check that add was called with level parameter
        add_calls = mock_logger.add.call_args_list
        assert any("level" in str(call) for call in add_calls)

    @patch("src.core.logging.logger")
    def test_setup_logging_custom_format(self, mock_logger):
        """Test setup_logging with custom format."""
        custom_format = "%(asctime)s - %(message)s"
        setup_logging(log_format=custom_format)
        # Check that add was called with format parameter
        add_calls = mock_logger.add.call_args_list
        assert any(custom_format in str(call) for call in add_calls)

    @patch("src.core.logging.logger")
    @patch("src.core.logging.logging")
    def test_setup_logging_configures_standard_logging(self, mock_logging, mock_logger):
        """Test that setup_logging configures standard library logging."""
        setup_logging()
        # Check that standard library loggers were configured
        assert mock_logging.getLogger.call_count >= 4


class TestGetLogger:
    """Test get_logger functionality."""

    @patch("src.core.logging.logger")
    def test_get_logger_with_name(self, mock_logger):
        """Test get_logger with a name."""
        get_logger("test_module")
        mock_logger.bind.assert_called_once_with(name="test_module")

    @patch("src.core.logging.logger")
    def test_get_logger_returns_bound_logger(self, mock_logger):
        """Test get_logger returns bound logger."""
        mock_bind = MagicMock(return_value=mock_logger)
        mock_logger.bind = mock_bind

        logger_instance = get_logger("test_module")
        assert logger_instance is not None


class TestLoggingContextFilter:
    """Test LoggingContextFilter."""

    def test_filter_initialization(self):
        """Test LoggingContextFilter initialization."""
        filter_instance = LoggingContextFilter()
        assert filter_instance.context == {}

    def test_filter_initialization_with_context(self):
        """Test LoggingContextFilter initialization with context."""
        context = {"request_id": "123", "user": "test"}
        filter_instance = LoggingContextFilter(context)
        assert filter_instance.context == context

    def test_filter_adds_context_to_record(self):
        """Test that filter adds context to log record."""
        context = {"request_id": "123", "user": "test"}
        filter_instance = LoggingContextFilter(context)

        record = MagicMock()
        result = filter_instance.filter(record)

        assert result is True
        assert hasattr(record, "request_id")
        assert hasattr(record, "user")

    def test_filter_empty_context(self):
        """Test filter with empty context."""
        filter_instance = LoggingContextFilter()
        record = MagicMock()
        result = filter_instance.filter(record)
        assert result is True


class TestLogRequestMiddleware:
    """Test log_request_middleware."""

    @pytest.mark.asyncio
    async def test_middleware_logs_request(self):
        """Test that middleware logs incoming request."""
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = "http://test.com/api/test"
        mock_request.client = MagicMock(host="127.0.0.1")
        mock_request.headers = MagicMock(get=lambda x, y=None: "test-agent" if x == "user-agent" else y)

        mock_response = MagicMock()
        mock_response.status_code = 200

        async def call_next(request):
            return mock_response

        with patch("src.core.logging.logger") as mock_logger:
            await log_request_middleware(mock_request, call_next)
            # Check that logger.info was called for request
            assert mock_logger.info.call_count >= 2

    @pytest.mark.asyncio
    async def test_middleware_returns_response(self):
        """Test that middleware returns response."""
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = "http://test.com/api/test"
        mock_request.client = MagicMock(host="127.0.0.1")
        mock_request.headers = MagicMock(get=lambda x, y=None: "test-agent" if x == "user-agent" else y)

        mock_response = MagicMock()
        mock_response.status_code = 200

        async def call_next(request):
            return mock_response

        response = await log_request_middleware(mock_request, call_next)
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_middleware_handles_no_client(self):
        """Test middleware handles request without client."""
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = "http://test.com/api/test"
        mock_request.client = None
        mock_request.headers = MagicMock(get=lambda x, y=None: "test-agent" if x == "user-agent" else y)

        mock_response = MagicMock()
        mock_response.status_code = 200

        async def call_next(request):
            return mock_response

        with patch("src.core.logging.logger"):
            response = await log_request_middleware(mock_request, call_next)
            assert response == mock_response

    @pytest.mark.asyncio
    async def test_middleware_logs_processing_time(self):
        """Test that middleware logs processing time."""
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = "http://test.com/api/test"
        mock_request.client = MagicMock(host="127.0.0.1")
        mock_request.headers = MagicMock(get=lambda x, y=None: "test-agent" if x == "user-agent" else y)

        mock_response = MagicMock()
        mock_response.status_code = 200

        async def call_next(request):
            return mock_response

        with patch("src.core.logging.logger") as mock_logger:
            await log_request_middleware(mock_request, call_next)
            # Check that logger.info was called with process_time
            info_calls = str(mock_logger.info.call_args_list)
            assert any("process_time" in call for call in info_calls)
