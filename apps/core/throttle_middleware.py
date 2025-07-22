"""Module implementation."""
import time

from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin


class RateLimitMiddleware(MiddlewareMixin):
    """Enhanced rate limiting middleware with analytics"""

    def process_request(self, request):
        # Skip for health checks
        if request.path in ["/health/", "/metrics/"]:
            return None

        # Track request for analytics
        self.track_request(request)

        # Add rate limit info to request
        request.rate_limit_info = self.get_rate_limit_info(request)

        return None

    def process_response(self, request, response):
        # Add rate limit headers
        if hasattr(request, "rate_limit_info"):
            info = request.rate_limit_info
            response["X-RateLimit-Limit"] = str(info.get("limit", 100))
            response["X-RateLimit-Remaining"] = str(info.get("remaining", 100))
            response["X-RateLimit-Reset"] = str(info.get("reset", 0))

            if info.get("retry_after"):
                response["Retry-After"] = str(info["retry_after"])

        return response

    def get_rate_limit_info(self, request):
        """Calculate rate limit info for current request."""
        if request.user.is_authenticated:
            key = f"rate_limit_user_{request.user.id}"
            limit = self.get_user_limit(request.user)
        else:
            key = f"rate_limit_ip_{self.get_client_ip(request)}"
            limit = 100

        # Get current usage
        window_start = int(time.time() // 3600) * 3600
        usage_key = f"{key}_{window_start}"
        current_usage = cache.get(usage_key, 0)

        remaining = max(0, limit - current_usage)
        reset = window_start + 3600

        info = {"limit": limit, "remaining": remaining, "reset": reset, "usage": current_usage}

        if remaining == 0:
            info["retry_after"] = reset - int(time.time())

        return info

    def get_user_limit(self, user):
        """Get rate limit based on user tier."""
        tier_limits = {
            "free": 100,
            "basic": 500,
            "premium": 2000,
            "enterprise": 10000,
        }
        tier = getattr(user, "tier", "free")
        return tier_limits.get(tier, 100)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    def track_request(self, request):
        """Track request for analytics."""
        analytics_key = "rate_limit_analytics"
        analytics = cache.get(analytics_key, {})

        hour = int(time.time() // 3600)
        endpoint = request.path

        if hour not in analytics:
            analytics[hour] = {}
        if endpoint not in analytics[hour]:
            analytics[hour][endpoint] = {"requests": 0, "throttled": 0}

        analytics[hour][endpoint]["requests"] += 1

        # Keep only last 24 hours
        cutoff = hour - 24
        analytics = {k: v for k, v in analytics.items() if k > cutoff}

        cache.set(analytics_key, analytics, 86400)
