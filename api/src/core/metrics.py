"""
Prometheus metrics collection for Split Bill API.
Provides business metrics, performance metrics, and system metrics for monitoring.
"""

import time

# Import prometheus with graceful degradation
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    print("Warning: prometheus_client not available, metrics will be disabled")
    PROMETHEUS_AVAILABLE = False

    # Create dummy classes for when prometheus is not available
    class Counter:
        def __init__(self, name: str, description: str, labelnames: list = None):
            self.name = name
            self.description = description
            self.labelnames = labelnames or []

        def inc(self, value: float = 1):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Histogram:
        def __init__(self, name: str, description: str, labelnames: list = None):
            self.name = name
            self.description = description
            self.labelnames = labelnames or []

        def observe(self, value: float):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Gauge:
        def __init__(self, name: str, description: str, labelnames: list = None):
            self.name = name
            self.description = description
            self.labelnames = labelnames or []

        def set(self, value: float):
            pass

        def inc(self, value: float = 1):
            pass

        def dec(self, value: float = 1):
            pass

        def labels(self, *args, **kwargs):
            return self

    def generate_latest():
        return b"# Prometheus metrics not available"

    CONTENT_TYPE_LATEST = "text/plain"


# Request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# Business metrics
splits_calculated_total = Counter(
    "splits_calculated_total",
    "Total number of bill splits calculated",
    ["split_type"],  # 'even' or 'individual'
)

receipts_processed_total = Counter(
    "receipts_processed_total",
    "Total number of receipts processed",
    ["status"],  # 'success' or 'error'
)

share_links_generated_total = Counter(
    "share_links_generated_total", "Total number of share links generated"
)

# Cache metrics
cache_operations_total = Counter(
    "cache_operations_total",
    "Total number of cache operations",
    ["operation", "status"],  # 'hit', 'miss', 'error'
)

cache_response_time_seconds = Histogram(
    "cache_response_time_seconds",
    "Cache operation response time in seconds",
    ["operation"],  # 'get', 'set', 'delete'
)

# OCR processing metrics
ocr_processing_duration_seconds = Histogram(
    "ocr_processing_duration_seconds",
    "OCR processing duration in seconds",
    ["status"],  # 'success', 'error'
)

# System metrics
active_connections = Gauge("active_connections", "Number of active connections")

memory_usage_mb = Gauge("memory_usage_mb", "Memory usage in megabytes")

cpu_usage_percent = Gauge("cpu_usage_percent", "CPU usage percentage")

# Health metrics
service_health_status = Gauge(
    "service_health_status",
    "Service health status (1=healthy, 0=unhealthy)",
    ["service"],  # 'redis', 'garage', 'openrouter', 'api'
)


class MetricsCollector:
    """Centralized metrics collection for the application."""

    def __init__(self):
        self.prometheus_available = PROMETHEUS_AVAILABLE
        self._start_time = time.time()

    def record_http_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics."""
        if not self.prometheus_available:
            return

        http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
            duration
        )

    def record_split_calculation(self, split_type: str):
        """Record bill split calculation."""
        if not self.prometheus_available:
            return

        splits_calculated_total.labels(split_type=split_type).inc()

    def record_receipt_processing(self, status: str):
        """Record receipt processing."""
        if not self.prometheus_available:
            return

        receipts_processed_total.labels(status=status).inc()

    def record_share_link_generation(self):
        """Record share link generation."""
        if not self.prometheus_available:
            return

        share_links_generated_total.inc()

    def record_cache_operation(self, operation: str, status: str, duration: float):
        """Record cache operation metrics."""
        if not self.prometheus_available:
            return

        cache_operations_total.labels(operation=operation, status=status).inc()

        cache_response_time_seconds.labels(operation=operation).observe(duration)

    def record_ocr_processing(self, status: str, duration: float):
        """Record OCR processing metrics."""
        if not self.prometheus_available:
            return

        ocr_processing_duration_seconds.labels(status=status).observe(duration)

    def update_active_connections(self, count: int):
        """Update active connections count."""
        if not self.prometheus_available:
            return

        active_connections.set(count)

    def update_memory_usage(self, usage_mb: float):
        """Update memory usage."""
        if not self.prometheus_available:
            return

        memory_usage_mb.set(usage_mb)

    def update_cpu_usage(self, usage_percent: float):
        """Update CPU usage."""
        if not self.prometheus_available:
            return

        cpu_usage_percent.set(usage_percent)

    def update_service_health(self, service: str, is_healthy: bool):
        """Update service health status."""
        if not self.prometheus_available:
            return

        service_health_status.labels(service=service).set(1 if is_healthy else 0)

    def get_metrics_text(self) -> str:
        """Get Prometheus metrics in text format."""
        if not self.prometheus_available:
            return (
                "# Prometheus metrics not available - prometheus_client not installed"
            )

        return generate_latest().decode("utf-8")

    def get_metrics_content_type(self) -> str:
        """Get Prometheus metrics content type."""
        return CONTENT_TYPE_LATEST if self.prometheus_available else "text/plain"


# Global metrics collector instance
metrics = MetricsCollector()


# Decorator for automatic HTTP request metrics
def track_http_metrics(endpoint_name: str = None):
    """Decorator to automatically track HTTP request metrics."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Extract method and endpoint from request if available
                method = "UNKNOWN"
                endpoint = endpoint_name or func.__name__
                status_code = 200

                # Try to get request from context
                for arg in args:
                    if hasattr(arg, "method") and hasattr(arg, "url"):
                        method = arg.method
                        endpoint = endpoint or str(arg.url.path)
                        break

                metrics.record_http_request(method, endpoint, status_code, duration)
                return result

            except Exception:
                duration = time.time() - start_time

                # Record error metrics
                method = "UNKNOWN"
                endpoint = endpoint_name or func.__name__
                status_code = 500

                for arg in args:
                    if hasattr(arg, "method") and hasattr(arg, "url"):
                        method = arg.method
                        endpoint = endpoint or str(arg.url.path)
                        break

                metrics.record_http_request(method, endpoint, status_code, duration)
                raise

        return wrapper

    return decorator


# Business metric tracking functions
def track_business_metrics(operation: str):
    """Decorator to track business metrics."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                if operation == "split_calculation":
                    # Try to determine split type from result
                    split_type = "unknown"
                    if hasattr(result, "split_evenly"):
                        split_type = "even" if result.split_evenly else "individual"
                    metrics.record_split_calculation(split_type)

                elif operation == "receipt_processing":
                    metrics.record_receipt_processing("success")

                elif operation == "share_link_generation":
                    metrics.record_share_link_generation()

                return result

            except Exception:
                if operation == "receipt_processing":
                    metrics.record_receipt_processing("error")
                raise

        return wrapper

    return decorator
