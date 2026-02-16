"""
Unit tests for core.sentry_config module.
Tests Sentry error tracking and observability.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.core.sentry_config import (
    SENTRY_AVAILABLE,
    SentryTracker,
    sentry_tracker,
    init_sentry,
    capture_error,
    capture_message,
    set_user_context,
    add_breadcrumb,
    track_performance,
    track_errors,
)


class TestSentryAvailability:
    """Test Sentry availability."""

    def test_sentry_available_flag(self):
        """Test SENTRY_AVAILABLE flag is set."""
        assert isinstance(SENTRY_AVAILABLE, bool)


class TestSentryTrackerInitialization:
    """Test SentryTracker initialization."""

    def test_sentry_tracker_initialization(self):
        """Test SentryTracker initialization."""
        tracker = SentryTracker()
        assert tracker.sentry_initialized is False
        assert hasattr(tracker, "dsn")
        assert hasattr(tracker, "environment")


class TestSentryTrackerInitialize:
    """Test SentryTracker initialize method."""

    @patch("src.core.sentry_config.sentry_sdk")
    def test_initialize_success(self, mock_sentry_sdk):
        """Test successful Sentry initialization."""
        mock_sentry_sdk.init = MagicMock()
        mock_sentry_sdk.configure_scope = MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock()))

        tracker = SentryTracker()
        tracker.dsn = "test-dsn"

        result = tracker.initialize()
        assert result is True
        assert tracker.sentry_initialized is True

    @patch("src.core.sentry_config.sentry_sdk")
    def test_initialize_no_dsn(self, mock_sentry_sdk):
        """Test initialize without DSN."""
        tracker = SentryTracker()
        tracker.dsn = None

        result = tracker.initialize()
        assert result is False
        assert tracker.sentry_initialized is False

    @patch("src.core.sentry_config.sentry_sdk")
    def test_initialize_exception(self, mock_sentry_sdk):
        """Test initialize with exception."""
        mock_sentry_sdk.init = MagicMock(side_effect=Exception("Init error"))
        mock_sentry_sdk.configure_scope = MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exitexit__=MagicMock()))

        tracker = SentryTracker()
        tracker.dsn = "test-dsn"

        result = tracker.initialize()
        assert result is False
        assert tracker.sentry_initialized is False


class TestSentryTrackerCaptureException:
    """Test SentryTracker capture_exception method."""

    @patch("src.core.sentry_config.sentry_sdk")
    def test_capture_exception_not_initialized(self, mock_sentry_sdk):
        """Test capture_exception when not initialized."""
        tracker = SentryTracker()
        tracker.sentry_initialized = False

        exception = ValueError("Test error")
        tracker.capture_exception(exception)
        # Should not call sentry_sdk methods

    @patch("src.core.sentry_config.sentry_sdk")
    def test_capture_exception_with_context(self, mock_sentry_sdk):
        """Test capture_exception with context."""
        mock_scope = MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock())
        mock_sentry_sdk.configure_scope = MagicMock(return_value=mock_scope)
        mock_sentry_sdk.capture_exception = MagicMock()

        tracker = SentryTracker()
        tracker.sentry_initialized = True

        exception = ValueError("Test error")
        context = {"user_id": "123", "action": "test"}

        tracker.capture_exception(exception, context)
        mock_sentry_sdk.capture_exception.assert_called_once()


class TestSentryTrackerCaptureMessage:
    """Test SentryTracker capture_message method."""

    @patch("src.core.sentry_config.sentry_sdk")
    def test_capture_message_not_initialized(self, mock_sentry_sdk):
        """Test capture_message when not initialized."""
        tracker = SentryTracker()
        tracker.sentry_initialized = False

        tracker.capture_message("Test message")
        # Should not call sentry_sdk methods

    @patch("src.core.sentry_config.sentry_sdk")
    def test_capture_message_with_level(self, mock_sentry_sdk):
        """Test capture_message with custom level."""
        mock_scope = MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock())
        mock_sentry_sdk.configure_scope = MagicMock(return_value=mock_scope)
        mock_sentry_sdk.capture_message = MagicMock()

        tracker = SentryTracker()
        tracker.sentry_initialized = True

        tracker.capture_message("Test message", level="warning")
        mock_sentry_sdk.capture_message.assert_called_once()


class TestSentryTrackerSetUserContext:
    """Test SentryTracker set_user_context method."""

    @patch("src.core.sentry_config.sentry_sdk")
    def test_set_user_context_not_initialized(self, mock_sentry_sdk):
        """Test set_user_context when not initialized."""
        tracker = SentryTracker()
        tracker.sentry_initialized = False

        tracker.set_user_context(user_id="123", email="test@example.com")
        # Should not call sentry_sdk methods

    @patch("src.core.sentry_config.sentry_sdk")
    def test_set_user_context_with_params(self, mock_sentry_sdk):
        """Test set_user_context with parameters."""
        mock_sentry_sdk.set_user = MagicMock()

        tracker = SentryTracker()
        tracker.sentry_initialized = True

        tracker.set_user_context(user_id="123", email="test@example.com")
        mock_sentry_sdk.set_user.assert_called_once()

    @patch("src.core.sentry_config.sentry_sdk")
    def test_set_user_context_with_kwargs(self, mock_sentry_sdk):
        """Test set_user_context with additional kwargs."""
        mock_sentry_sdk.set_user = MagicMock()

        tracker = SentryTracker()
        tracker.sentry_initialized = True

        tracker.set_user_context(user_id="123", username="testuser")
        mock_sentry_sdk.set_user.assert_called_once()


class TestSentryTrackerAddBreadcrumb:
    """Test SentryTracker add_breadcrumb method."""

    @patch("src.core.sentry_config.sentry_sdk")
    def test_add_breadcrumb_not_initialized(self, mock_sentry_sdk):
        """Test add_breadcrumb when not initialized."""
        tracker = SentryTracker()
        tracker.sentry_initialized = False



        tracker.add_breadcrumb("Test message")
        # Should not call sentry_sdk methods

    @patch("src.core.sentry_config.sentry_sdk")
    def test_add_breadcrumb_with_params(self, mock_sentry_sdk):
        """Test add_breadcrumb with parameters."""
        mock_sentry_sdk.add_breadcrumb = MagicMock()

        tracker = SentryTracker()
        tracker.sentry_initialized = True

        tracker.add_breadcrumb("Test message", category="custom", level="info")
        mock_sentry_sdk.add_breadcrumb.assert_called_once()


class TestSentryTrackerTrackPerformance:
    """Test SentryTracker track_performance method."""

    @patch("src.core.sentry_config.sentry_sdk")
    def test_track_performance_not_initialized(self, mock_sentry_sdk):
        """Test track_performance when not initialized."""
        tracker = SentryTracker()
        tracker.sentry_initialized = False

        tracker.track_performance("test_operation", 123.45)
        # Should not call sentry_sdk methods

    @patch("src.core.sentry_config.sentry_sdk")
    def test_track_performance_success(self, mock_sentry_sdk):
        """Test track_performance for successful operation."""
        mock_scope = MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock())
        mock_sentry_sdk.configure_scope = MagicMock(return_value=mock_scope)
        mock_sentry_sdk.capture_message = MagicMock()

        tracker = SentryTracker()
        tracker.sentry_initialized = True

        tracker.track_performance("test_operation", 123.45, success=True)
        mock_sentry_sdk.capture_message.assert_called()

    @patch("src.core.sentry_config.sentry_sdk")
    def test_track_performance_failure(self, mock_sentry_sdk):
        """Test track_performance for failed operation."""
        mock_scope = MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock())
        mock_sentry_sdk.configure_scope = MagicMock(return_value=mock_scope)
        mock_sentry_sdk.capture_message = MagicMock()

        tracker = SentryTracker()
        tracker.sentry_initialized = True

        tracker.track_performance("test_operation", 123.45, success=False)
        mock_sentry_sdk.capture_message.assert_called()


class TestGlobalSentryTrackerInstance:
    """Test global sentry_tracker instance."""

    def test_global_sentry_tracker_exists(self):
        """Test that global sentry_tracker instance exists."""
        assert sentry_tracker is not None
        assert isinstance(sentry_tracker, SentryTracker)


class TestInitSentryFunction:
    """Test init_sentry function."""

    @patch("src.core.sentry_config.sentry_tracker")
    def test_init_sentry(self, mock_tracker):
        """Test init_sentry function."""
        mock_tracker.initialize = MagicMock(return_value=True)

        result = init_sentry()
        mock_tracker.initialize.assert_called_once()
        assert result is True


class TestCaptureErrorFunction:
    """Test capture_error function."""

    @patch("src.core.sentry_config.sentry_tracker")
    def test_capture_error(self, mock_tracker):
        """Test capture_error function."""
        exception = ValueError("Test error")
        context = {"user_id": "123"}

        capture_error(exception, context)
        mock_tracker.capture_exception.assert_called_once_with(exception, context)


class TestCaptureMessageFunction:
    """Test capture_message function."""

    @patch("src.core.sentry_config.sentry_tracker")
    def test_capture_message(self, mock_tracker):
        """Test capture_message function."""
        capture_message("Test message", level="info", context={"key": "value"})
        mock_tracker.capture_message.assert_called_once()


class TestSetUserContextFunction:
    """Test set_user_context function."""

    @patch("src.core.sentry_config.sentry_tracker")
    def test_set_user_context(self, mock_tracker):
        """Test set_user_context function."""
        set_user_context(user_id="123", email="test@example.com", username="testuser")
        mock_tracker.set_user_context.assert_called_once()


class TestAddBreadcrumbFunction:
    """Test add_breadcrumb function."""

    @patch("src.core.sentry_config.sentry_tracker")
    def test_add_breadcrumb(self, mock_tracker):
        """Test add_breadcrumb function."""
        add_breadcrumb("Test message", category="custom", level="info")
        mock_tracker.add_breadcrumb.assert_called_once()


class TestTrackPerformanceFunction:
    """Test track_performance function."""

    @patch("src.core.sentry_config.sentry_tracker")
    def test_track_performance(self, mock_tracker):
        """Test track_performance function."""
        track_performance("test_operation", 123.45, success=True, context={"key": "value"})
        mock_tracker.track_performance.assert_called_once()


class TestTrackErrorsDecorator:
    """Test track_errors decorator."""

    @pytest.mark.asyncio
    @patch("src.core.sentry_config.track_performance")
    @patch("src.core.sentry_config.capture_error")
    async def test_track_errors_success(self, mock_capture_error, mock_track_performance):
        """Test track_errors decorator on successful function."""
        @track_errors("test_operation")
        async def test_func():
            return "result"

        result = await test_func()
        assert result == "result"
        mock_track_performance.assert_called()

    @pytest.mark.asyncio
    @patch("src.core.sentry_config.track_performance")
    @patch("src.core.sentry_config.capture_error")
    async def test_track_errors_failure(self, mock_capture_error, mock_track_performance):
        """Test track_errors decorator on function that raises error."""
        @track_errors("test_operation")
        async def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await test_func()
        mock_capture_error.assert_called()
        mock_track_performance.assert_called()
