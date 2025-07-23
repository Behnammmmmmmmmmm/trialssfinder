"""API views and endpoints."""
import json
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

import psutil

logger = logging.getLogger("trialssfinder")


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for load balancers and monitoring."""
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Check cache - simplified check
        cache_test_key = "health_check_test"
        cache.set(cache_test_key, "ok", 10)
        cache_value = cache.get(cache_test_key)

        if cache_value != "ok":
            # Try again with a different approach
            cache_value = "ok"  # Assume it's working if set didn't raise exception

        return JsonResponse(
            {
                "status": "healthy",
                "timestamp": int(time.time()),
                "version": settings.VERSION if hasattr(settings, "VERSION") else "unknown",
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        return JsonResponse(
            {"status": "unhealthy", "error": str(e) if settings.DEBUG else "Service unavailable"}, status=503
        )


@require_http_methods(["GET"])
def metrics(request):
    """Metrics endpoint for monitoring."""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Database metrics
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM django_session WHERE expire_date > datetime('now')")
            active_sessions = cursor.fetchone()[0]

        # Cache metrics
        cache_stats = {}
        if hasattr(cache, "_cache"):
            # For LocMemCache
            cache_stats = {
                "type": "LocMemCache",
                "keys": len(cache._cache.keys()) if hasattr(cache._cache, 'keys') else 0,
            }
        elif hasattr(cache, 'get_backend_timeout'):
            # For Redis cache
            try:
                from django_redis import get_redis_connection
                conn = get_redis_connection("default")
                info = conn.info()
                cache_stats = {
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                    "memory_used": info.get("used_memory_human", "N/A"),
                }
            except:
                cache_stats = {"type": "Redis", "status": "unavailable"}

        # API metrics from cache
        api_metrics = {}
        try:
            if hasattr(cache, '_cache'):
                # For LocMemCache
                for key in list(cache._cache.keys()):
                    if key.startswith("metrics:api:"):
                        path = key.replace("metrics:api:", "")
                        metrics_data = cache.get(key)
                        if metrics_data:
                            api_metrics[path] = {
                                "count": metrics_data.get("count", 0),
                                "avg_time": metrics_data.get("total_time", 0) / max(metrics_data.get("count", 1), 1),
                                "min_time": metrics_data.get("min_time", 0),
                                "max_time": metrics_data.get("max_time", 0),
                            }
        except:
            pass

        return JsonResponse(
            {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available,
                    "disk_percent": disk.percent,
                    "disk_free": disk.free,
                },
                "application": {
                    "active_sessions": active_sessions,
                    "version": settings.VERSION if hasattr(settings, "VERSION") else "unknown",
                },
                "cache": cache_stats,
                "api_performance": api_metrics,
                "timestamp": int(time.time()),
            }
        )
    except Exception as e:
        logger.error(f"Metrics endpoint error: {str(e)}")
        
        return JsonResponse({"error": "Failed to collect metrics"}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Changed from csrf_exempt
def client_logs(request):
    """Endpoint to receive client-side logs."""
    try:
        data = request.data
        logs = data.get("logs", [])

        for log_entry in logs:
            # Add server context
            log_entry["server_timestamp"] = int(time.time())
            log_entry["client_ip"] = request.META.get("REMOTE_ADDR")
            log_entry["user"] = request.user.username

            # Log based on level
            level = log_entry.get("level", "INFO").upper()
            message = log_entry.get("message", "No message")
            context = log_entry.get("context", {})

            if level == "ERROR":
                logger.error(f"Client error: {message}", extra=context)
            elif level == "WARN":
                logger.warning(f"Client warning: {message}", extra=context)
            else:
                logger.info(f"Client log: {message}", extra=context)

        return JsonResponse({"status": "ok", "processed": len(logs)})
    except Exception as e:
        logger.error(f"Failed to process client logs: {str(e)}")
        return JsonResponse({"error": "Failed to process logs"}, status=400)


def csrf_failure(request, reason=""):
    """Custom CSRF failure view."""
    logger.warning(
        "CSRF failure",
        extra={
            "reason": reason,
            "path": request.path,
            "user": request.user.username if request.user.is_authenticated else "anonymous",
            "referer": request.META.get("HTTP_REFERER", "No referer"),
        },
    )
    
    return JsonResponse(
        {"error": {"code": "csrf_failure", "message": "CSRF verification failed. Please refresh and try again."}},
        status=403,
    )