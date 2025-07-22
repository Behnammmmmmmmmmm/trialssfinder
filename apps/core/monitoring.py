"""Module implementation."""
import logging
import time
from typing import Any, Dict

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

import psutil

logger = logging.getLogger("trialssfinder.monitoring")


class HealthCheck:
    @staticmethod
    def check_database() -> Dict[str, Any]:
        try:
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            latency = (time.time() - start_time) * 1000
            return {"status": "healthy", "latency_ms": round(latency, 2)}
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    def check_cache() -> Dict[str, Any]:
        try:
            start_time = time.time()
            cache.set("health_check", "ok", 10)
            value = cache.get("health_check")
            latency = (time.time() - start_time) * 1000

            if value == "ok":
                return {"status": "healthy", "latency_ms": round(latency, 2)}
            else:
                return {"status": "unhealthy", "error": "Cache read/write failed"}
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    def check_system_resources() -> Dict[str, Any]:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "status": "healthy" if cpu_percent < 90 and memory.percent < 90 else "warning",
            }
        except Exception as e:
            logger.error(f"System resources check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring services."""
    checks = {
        "database": HealthCheck.check_database(),
        "cache": HealthCheck.check_cache(),
        "system": HealthCheck.check_system_resources(),
    }

    overall_status = "healthy"
    for check_name, check_result in checks.items():
        if check_result.get("status") == "unhealthy":
            overall_status = "unhealthy"
            break
        elif check_result.get("status") == "warning":
            overall_status = "warning"

    response_data = {"status": overall_status, "checks": checks, "timestamp": time.time()}

    status_code = 200 if overall_status == "healthy" else 503
    return JsonResponse(response_data, status=status_code)


@require_http_methods(["GET"])
def metrics(request):
    """Metrics endpoint for monitoring services."""
    try:
        metrics_data = {
            "requests": {
                "total": cache.get("metrics:requests:total", 0),
                "errors": cache.get("metrics:requests:errors", 0),
                "avg_duration_ms": cache.get("metrics:requests:avg_duration", 0),
            },
            "database": {
                "queries": len(connection.queries),
                "connections": connection.queries_log.count if hasattr(connection, "queries_log") else 0,
            },
            "cache": {
                "hits": cache.get("metrics:cache:hits", 0),
                "misses": cache.get("metrics:cache:misses", 0),
            },
            "system": HealthCheck.check_system_resources(),
            "timestamp": time.time(),
        }

        return JsonResponse(metrics_data)
    except Exception as e:
        logger.error(f"Metrics endpoint error: {str(e)}")
        return JsonResponse({"error": "Failed to collect metrics"}, status=500)
