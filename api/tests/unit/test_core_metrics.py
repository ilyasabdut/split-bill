"""
Unit tests for core.metrics module.
Tests Prometheus metrics collection.
"""

from unittest.mock import MagicMock

import pytest

from src.core.metrics import (
    PROMETHEUS_AVAILABLE,
    Counter,
    Gauge,
    Histogram,
    http_requests_total,
    http_request_duration_seconds,
    splits_calculated_total,
    receipts_processed_total,
    share_links_generated_total,
    cache_operations_total,
    cache_response_time_seconds,
    ocr_processing_duration_seconds,
    active_connections,
    memory_usage_mb,
    cpu_usage_percent,
    service_health_status,
    MetricsCollector,
    metrics,
    track_http_metrics,
    track_business_metrics,
)


class TestPrometheusAvailability:
    """Test Prometheus availability."""

    def test_prometheus_available_flag(self):
        """Test PROMETHEUS_AVAILABLE flag is set."""
        assert isinstance(PROMETHEUS_AVAILABLE, bool)

    def test_counter_exists(self):
        """Test Counter instances exist."""
        assert http_requests_total is not None
        assert splits_calculated_total is not None
        assert receipts_processed_total is not None
        assert share_links_generated_total is not None
        assert cache_operations_total is not None

    def test_gauge_exists(self):
        """Test Gauge instances exist."""
        assert active_connections is not None
        assert memory_usage_mb is not None
        assert cpu_usage_percent is not None
        assert service_health_status is not None

    def test_histogram_exists(self):
        """Test Histogram instances exist."""
        assert http_request_duration_seconds is not None
        assert cache_response_time_seconds is not None
        assert ocr_processing_duration_seconds is not None


class TestDummyMetrics:
    """Test dummy metrics when Prometheus is not available."""

    @pytest.mark.skipif(PROMETHEUS_AVAILABLE, reason="Prometheus is available")
    def test_dummy_counter_inc(self):
        """Test dummy Counter inc method."""
        counter = Counter("test", "test counter")
        counter.inc(1.0)
        counter.inc(5.0)
        # Should not raise any errors

    @pytest.mark.skipif(PROMETHEUS_AVAILABLE, reason="Prometheus is available")
    def test_dummy_counter_labels(self):
        """Test dummy Counter labels method."""
        counter = Counter("test", "test counter")
        labeled = counter.labels("label1", "label2")
        labeled.inc(1.0)
        # Should not raise any errors

    @pytest.mark.skipif(PROMETHEUS_AVAILABLE, reason="Prometheus is available")
    def test_dummy_gauge_set(self):
        """Test dummy Gauge set method."""
        gauge = Gauge("test", "test gauge")
        gauge.set(100.0)
        # Should not raise any errors

    @pytest.mark.skipif(PROMETHEUS_AVAILABLE, reason="Prometheus is available")
    def test_dummy_gauge_inc_dec(self):
        """Test dummy Gauge inc/dec methods."""
        gauge = Gauge("test", "test gauge")
        gauge.inc(1.0)
        gauge.dec(1.0)
        # Should not raise any errors

    @pytest.mark.skipif(PROMETHEUS_AVAILABLE, reason="Prometheus is available")
    def test_dummy_histogram_observe(self):
        """Test dummy Histogram observe method."""
        histogram = Histogram("test", "test histogram")
        histogram.observe(123.45)
        # Should not raise any errors


class TestMetricsCollector:
    """Test MetricsCollector class."""

    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()
        assert collector.prometheus_available == PROMETHEUS_AVAILABLE
        assert hasattr(collector, "_start_time")

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_record_http_request(self):
        """Test record_http_request method."""
        collector = MetricsCollector()
        collector.record_http_request("GET", "/api/test", 200, 0.123)
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_record_split_calculation(self):
        """Test record_split_calculation method."""
        collector = MetricsCollector()
        collector.record_split_calculation("even")
        collector.record_split_calculation("individual")
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_record_receipt_processing(self):
        """Test record_receipt_processing method."""
        collector = MetricsCollector()
        collector.record_receipt_processing("success")
        collector.record_receipt_processing("error")
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_record_share_link_generation(self):
        """Test record_share_link_generation method."""
        collector = MetricsCollector()
        collector.record_share_link_generation()
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_record_cache_operation(self):
        """Test record_cache_operation method."""
        collector = MetricsCollector()
        collector.record_cache_operation("get", "hit", 0.045)
        collector.record_cache_operation("set", "success", 0.012)
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_record_ocr_processing(self):
        """Test record_ocr_processing method."""
        collector = MetricsCollector()
        collector.record_ocr_processing("success", 1.234)
        collector.record_ocr_processing("error", 0.567)
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_update_active_connections(self):
        """Test update_active_connections method."""
        collector = MetricsCollector()
        collector.update_active_connections(10)
        collector.update_active_connections(5)
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_update_memory_usage(self):
        """Test update_memory_usage method."""
        collector = MetricsCollector()
        collector.update_memory_usage(256.5)
        collector.update_memory_usage(512.0)
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_update_cpu_usage(self):
        """Test update_cpu_usage method."""
        collector = MetricsCollector()
        collector.update_cpu_usage(45.5)
        collector = update_cpu_usage(78.2)
        # Should not raise any errors

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_update_service_health(self):
        """Test update_service_health method."""
        collector = MetricsCollector()
        collector.update_service_health("redis", True)
        collector.update_service_health("redis", False)
        # Should not raise any errors

    def test_get_metrics_text(self):
        """Test get_metrics_text method."""
        collector = MetricsCollector()
        metrics_text = collector.get_metrics_text()
        assert isinstance(metrics_text, str)
        assert len(metrics_text) > 0

    def test_get_metrics_content_type(self):
        """Test get_metrics_content_type method."""
        collector = MetricsCollector()
        content_type = collector.get_metrics_content_type()
        assert isinstance(content_type, str)
        assert "text" in content_type.lower() or "application" in content_type.lower()


class TestGlobalMetricsInstance:
    """Test global metrics instance."""

    def test_global_metrics_instance_exists(self):
        """Test that global metrics instance exists."""
        assert metrics is not None
        assert isinstance(metrics, MetricsCollector)


class TestTrackHttpMetricsDecorator:
    """Test track_http_metrics decorator."""

    @pytest.mark.asyncio
    async def test_track_http_metrics_success(self):
        """Test track_http_metrics on successful function."""
        @track_http_metrics("test_endpoint")
        async def test_func():
            return "result"

        result = await test_func()
        assert result == "result"

    @pytest.mark.asyncio
    async def test_track_http_metrics_error(self):
        """Test track_http_metrics on function that raises error."""
        @track_http_metrics("test_endpoint")
        async def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await test_func()

    @pytest.mark.asyncio
    async def test_track_http_metrics_with_request(self):
        """Test track_http_metrics with request object."""
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = MagicMock(path="/api/test")

        @track_http_metrics("test_endpoint")
        async def test_func(request):
            return "result"

        result = await test_func(mock_request)
        assert result == "result"


class TestTrackBusinessMetricsDecorator:
    """Test track_business_metrics decorator."""

    @pytest.mark.asyncio
    async def test_track_business_metrics_split_calculation(self):
        """Test track_business_metrics for split_calculation."""
        @track_business_metrics("split_calculation")
        async def test_func():
            return type("Result", (), {"split_evenly": True})()

        result = await test_func()
        assert result is not None

    @pytest.mark.asyncio
    async def test_track_business_metrics_receipt_processing(self):
        """Test track_business_metrics for receipt_processing."""
        @track_business_metrics("receipt_processing")
        async def test_func():
            return "result"

        result = await test_func()
        assert result == "result"

    @pytest.mark.asyncio
    async def test_track_business_metrics_receipt_processing_error(self):
        """Test track_business_metrics for receipt_processing with error."""
        @track_business_metrics("receipt_processing")
        async def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await test_func()

    @pytest.mark.asyncio
    async def test_track_business_metrics_share_link_generation(self):
        """Test track_business_metrics for share_link_generation."""
        @track_business_metrics("share_link_generation")
        async def test_func():
            return "result"

        result = await test_func()
        assert result == "result"


class TestMetricLabels:
    """Test metric labels."""

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_http_requests_total_labels(self):
        """Test http_requests_total has correct labels."""
        assert hasattr(http_requests_total, "labelnames")
        labels = http_requests_total.labelnames
        assert "method" in labels
        assert "endpoint" in labels
        assert "status_code" in labels

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_http_request_duration_labels(self):
        """Test http_request_duration_seconds has correct labels."""
        assert hasattr(http_request_duration_seconds, "labelnames")
        labels = http_request_duration_seconds.labelnames
        assert "method" in labels
        assert "endpoint" in labels

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_splits_calculated_labels(self):
        """Test splits_calculated_total has correct labels."""
        assert hasattr(splits_calculated_total, "labelnames")
        labels = splits_calculated_total.labelnames
        assert "split_type" in labels

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_receipts_processed_labels(self):
        """Test receipts_processed_total has correct labels."""
        assert hasattr(receipts_processed_total, "labelnames")
        labels = receipts_processed_total.labelnames
        assert "status" in labels

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_cache_operations_labels(self):
        """Test cache_operations_total has correct labels."""
        assert hasattr(cache_operations_total, "labelnames")
        labels = cache_operations_total.labelnames
        assert "operation" in labels
        assert "status" in labels

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_ocr_processing_labels(self):
        """Test ocr_processing_duration_seconds has correct labels."""
        assert hasattr(ocr_processing_duration_seconds, "labelnames")
        labels = ocr_processing_duration_seconds.labelnames
        assert "status" in labels

    @pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
    def test_service_health_status_labels(self):
        """Test service_health_status has correct labels."""
        assert hasattr(service_health_status, "labelnames")
        labels = service_health_status.labelnames
        assert "service" in labels
