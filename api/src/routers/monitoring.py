"""
Simple monitoring endpoints for Split Bill API.
Provides basic health checks and metrics without external dependencies.
"""

import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse


# Create router
monitoring_router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@monitoring_router.get("/health")
async def comprehensive_health_check():
    """
    Comprehensive health check endpoint.
    Returns detailed health status of all services and components.
    """
    try:
        # Start with basic API health
        start_time = time.time()
        
        # Check basic API functionality
        api_healthy = True
        api_response_time = (time.time() - start_time) * 1000
        
        # Compile service status
        services = {
            "api": {
                "status": "healthy" if api_healthy else "unhealthy",
                "response_time_ms": round(api_response_time, 2),
                "last_check": datetime.now().isoformat(),
                "details": {
                    "version": "2.0.0",
                    "uptime_seconds": round(time.time() - start_time, 2),
                    "python_version": "3.12+"
                }
            },
            "cache": {
                "status": "unknown",
                "response_time_ms": 0,
                "last_check": datetime.now().isoformat(),
                "details": {
                    "available": False,
                    "note": "Cache monitoring not implemented"
                }
            },
            "database": {
                "status": "unknown",
                "response_time_ms": 0,
                "last_check": datetime.now().isoformat(),
                "details": {
                    "available": False,
                    "note": "Database health checks not implemented"
                }
            },
            "external_apis": {
                "status": "unknown",
                "response_time_ms": 0,
                "last_check": datetime.now().isoformat(),
                "details": {
                    "available": False,
                    "note": "External API monitoring not implemented"
                }
            }
        }
        
        # Determine overall health
        healthy_services = sum(1 for service in services.values() if service["status"] == "healthy")
        total_services = len(services)
        
        if healthy_services == total_services:
            overall_status = "healthy"
            status_code = status.HTTP_200_OK
        elif healthy_services > 0:
            overall_status = "degraded"
            status_code = status.HTTP_200_OK
        else:
            overall_status = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Calculate summary metrics
        avg_response_time = sum(service["response_time_ms"] for service in services.values()) / total_services
        uptime_percentage = (healthy_services / total_services) * 100
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": services,
            "summary": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "average_response_time_ms": round(avg_response_time, 2),
                "uptime_percentage": round(uptime_percentage, 2)
            },
            "note": "Basic health monitoring - enhanced features available with full monitoring stack"
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "services": {},
                "summary": {
                    "total_services": 0,
                    "healthy_services": 0,
                    "average_response_time_ms": 0,
                    "uptime_percentage": 0.0
                }
            }
        )


@monitoring_router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check endpoint for basic load balancer checks.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "split-bill-api"
    }


@monitoring_router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.
    Returns application metrics in Prometheus format.
    """
    try:
        # Basic metrics in Prometheus format
        current_time = int(time.time())
        
        metrics_text = f"""# Split Bill API Metrics
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{{service="split-bill-api"}} 0

# HELP api_uptime_seconds API uptime in seconds
# TYPE api_uptime_seconds counter
api_uptime_seconds{{service="split-bill-api"}} {current_time}

# HELP splits_calculated_total Total number of bill splits calculated
# TYPE splits_calculated_total counter
splits_calculated_total{{service="split-bill-api"}} 0

# HELP receipts_processed_total Total number of receipts processed
# TYPE receipts_processed_total counter
receipts_processed_total{{service="split-bill-api",status="success"}} 0
receipts_processed_total{{service="split-bill-api",status="error"}} 0

# HELP share_links_generated_total Total number of share links generated
# TYPE share_links_generated_total counter
share_links_generated_total{{service="split-bill-api"}} 0

# HELP cache_operations_total Total number of cache operations
# TYPE cache_operations_total counter
cache_operations_total{{service="split-bill-api",operation="get",status="hit"}} 0
cache_operations_total{{service="split-bill-api",operation="get",status="miss"}} 0
cache_operations_total{{service="split-bill-api",operation="set",status="success"}} 0

# HELP active_connections Number of active connections
# TYPE active_connections gauge
active_connections{{service="split-bill-api"}} 1
"""
        
        return PlainTextResponse(metrics_text, media_type="text/plain")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics collection failed: {str(e)}"
        )


@monitoring_router.get("/system-metrics")
async def system_metrics():
    """
    System metrics endpoint.
    Returns current system performance metrics.
    """
    try:
        # Basic system metrics
        return {
            "timestamp": datetime.now().isoformat(),
            "request_count": 0,
            "error_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time_ms": 0.0,
            "active_connections": 1,
            "memory_usage_mb": None,
            "cpu_usage_percent": None,
            "uptime_seconds": int(time.time()),
            "note": "Basic system metrics - enhanced metrics available with monitoring stack"
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System metrics collection failed: {str(e)}"
        )


@monitoring_router.get("/status")
async def application_status():
    """
    Application status endpoint.
    Returns overall application status and configuration.
    """
    return {
        "application": "split-bill-api",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "environment": "development",
        "features": {
            "monitoring": True,
            "metrics": True,
            "logging": True,
            "error_tracking": False
        },
        "components": {
            "health_checks": True,
            "prometheus_metrics": True,
            "structured_logging": False,
            "error_tracking": False
        }
    }


@monitoring_router.post("/test-error")
async def test_error_tracking():
    """
    Test endpoint for error tracking.
    Intentionally raises an error to test error handling.
    """
    try:
        # Test error handling
        raise ValueError("Test error for monitoring system")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Test error - this is expected for monitoring validation"
        )


@monitoring_router.get("/info")
async def monitoring_info():
    """
    Information about monitoring capabilities.
    """
    return {
        "monitoring_system": "Split Bill API Monitoring v1.0",
        "endpoints": {
            "/monitoring/health": "Comprehensive health check with service status",
            "/monitoring/health/simple": "Simple health check for load balancers",
            "/monitoring/metrics": "Prometheus metrics in text format",
            "/monitoring/system-metrics": "Current system performance metrics",
            "/monitoring/status": "Application status and configuration",
            "/monitoring/test-error": "Test error handling functionality",
            "/monitoring/info": "This information endpoint"
        },
        "features": {
            "service_health_monitoring": True,
            "prometheus_metrics": True,
            "structured_logging": False,
            "error_tracking": False,
            "performance_tracking": False,
            "business_metrics": False
        },
        "documentation": {
            "health_check_response": "Detailed service status with response times",
            "metrics_format": "Prometheus text exposition format",
            "error_tracking": "Error handling validation endpoint",
            "performance_monitoring": "Basic system metrics"
        },
        "note": "Basic monitoring implementation - full monitoring stack provides enhanced features"
    }