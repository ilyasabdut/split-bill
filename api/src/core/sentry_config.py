"""
Sentry error tracking and observability for Split Bill API.
Provides exception tracking, performance monitoring, and error alerting.
"""

import logging
import os
import time
from typing import Any, Dict

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    print("Warning: sentry_sdk not available, error tracking will be disabled")
    SENTRY_AVAILABLE = False
    sentry_sdk = None
    LoggingIntegration = None


class SentryTracker:
    """Sentry error tracking and observability."""

    def __init__(self):
        self.sentry_initialized = False
        self.dsn = os.environ.get("SENTRY_DSN")
        self.environment = os.environ.get("ENVIRONMENT", "development")

    def initialize(self):
        """Initialize Sentry if DSN is provided."""
        if not SENTRY_AVAILABLE or not self.dsn:
            print(
                "Sentry not initialized - DSN not available or sentry_sdk not installed"
            )
            return False

        try:
            # Configure Sentry
            sentry_logging = LoggingIntegration(
                level=logging.INFO, event_level=logging.ERROR
            )

            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                integrations=[sentry_logging],
                traces_sample_rate=1.0,  # Capture all traces for monitoring
                profiles_sample_rate=1.0,  # Capture performance profiles
                before_send=self._before_send,
                before_send_transaction=self._before_send_transaction,
            )

            self.sentry_initialized = True
            print("✅ Sentry error tracking initialized")
            return True

        except Exception as e:
            print(f"Failed to initialize Sentry: {e}")
            return False

    def _before_send(self, event, hint):
        """Filter and modify events before sending to Sentry."""
        # Add custom context
        if "extra" not in event:
            event["extra"] = {}

        event["extra"]["application"] = "split-bill-api"
        event["extra"]["environment"] = self.environment

        # Filter out health check errors to reduce noise
        if (
            event.get("transaction") == "/health"
            or event.get("transaction") == "/health/"
        ):
            return None

        return event

    def _before_send_transaction(self, transaction_event, hint):
        """Filter transactions before sending to Sentry."""
        # Only send performance data for actual API endpoints
        transaction_name = transaction_event.get("transaction", "")
        if transaction_name.startswith("/health") or transaction_name.startswith(
            "/metrics"
        ):
            return None

        return transaction_event

    def capture_exception(self, exception: Exception, context: Dict[str, Any] = None):
        """Capture an exception with optional context."""
        if not self.sentry_initialized:
            return

        with sentry_sdk.configure_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)

            sentry_sdk.capture_exception(exception)

    def capture_message(
        self, message: str, level: str = "info", context: Dict[str, Any] = None
    ):
        """Capture a message with optional context."""
        if not self.sentry_initialized:
            return

        with sentry_sdk.configure_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)

            sentry_sdk.capture_message(message, level=level)

    def set_user_context(self, user_id: str = None, email: str = None, **kwargs):
        """Set user context for error tracking."""
        if not self.sentry_initialized:
            return

        user_context = {}
        if user_id:
            user_context["id"] = user_id
        if email:
            user_context["email"] = email

        user_context.update(kwargs)
        sentry_sdk.set_user(user_context)

    def add_breadcrumb(
        self, message: str, category: str = "custom", level: str = "info"
    ):
        """Add a breadcrumb for context."""
        if not self.sentry_initialized:
            return

        sentry_sdk.add_breadcrumb(
            message=message, category=category, level=level, timestamp=time.time()
        )

    def track_performance(
        self,
        operation_name: str,
        start_time: float,
        success: bool = True,
        context: Dict[str, Any] = None,
    ):
        """Track performance metrics."""
        if not self.sentry_initialized:
            return

        duration = (time.time() - start_time) * 1000  # Convert to milliseconds

        with sentry_sdk.configure_scope() as scope:
            scope.set_extra("operation_name", operation_name)
            scope.set_extra("duration_ms", duration)
            scope.set_extra("success", success)

            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)

            if success:
                sentry_sdk.capture_message(
                    f"Performance: {operation_name} completed in {duration:.2f}ms",
                    level="info",
                )
            else:
                sentry_sdk.capture_message(
                    f"Performance: {operation_name} failed after {duration:.2f}ms",
                    level="error",
                )


# Global Sentry tracker instance
sentry_tracker = SentryTracker()


def init_sentry():
    """Initialize Sentry tracking."""
    return sentry_tracker.initialize()


def capture_error(error: Exception, context: Dict[str, Any] = None):
    """Capture an error with context."""
    sentry_tracker.capture_exception(error, context)


def capture_message(message: str, level: str = "info", context: Dict[str, Any] = None):
    """Capture a message."""
    sentry_tracker.capture_message(message, level, context)


def set_user_context(user_id: str = None, email: str = None, **kwargs):
    """Set user context for error tracking."""
    sentry_tracker.set_user_context(user_id, email, **kwargs)


def add_breadcrumb(message: str, category: str = "custom", level: str = "info"):
    """Add a breadcrumb for context."""
    sentry_tracker.add_breadcrumb(message, category, level)


def track_performance(
    operation_name: str,
    start_time: float,
    success: bool = True,
    context: Dict[str, Any] = None,
):
    """Track performance metrics."""
    sentry_tracker.track_performance(operation_name, start_time, success, context)


# Decorator for automatic error tracking
def track_errors(operation_name: str = None):
    """Decorator to automatically track errors and performance."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            try:
                result = await func(*args, **kwargs)

                # Track successful operation
                track_performance(op_name, start_time, success=True)

                return result

            except Exception as e:
                # Track failed operation
                track_performance(op_name, start_time, success=False)

                # Capture error with context
                error_context = {
                    "function": func.__name__,
                    "args": str(args)[:500],  # Limit length
                    "kwargs": str(kwargs)[:500],
                }
                capture_error(e, error_context)

                raise

        return wrapper

    return decorator
