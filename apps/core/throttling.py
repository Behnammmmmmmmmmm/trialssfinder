"""Module implementation."""
import time

from django.conf import settings
from django.core.cache import cache
from rest_framework.throttling import BaseThrottle, SimpleRateThrottle


class TierBasedRateThrottle(BaseThrottle):
    """Dynamic rate limiting based on user tiers"""

    tier_rates = {
        "free": "100/hour",
        "basic": "500/hour",
        "premium": "2000/hour",
        "enterprise": "10000/hour",
    }

    def get_user_tier(self, request) -> str:
        if not request.user.is_authenticated:
            return "anonymous"
        return getattr(request.user, "tier", "free")

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.id
        else:
            ident = self.get_ident(request)

        return f"throttle_{self.scope}_{ident}"

    def get_rate(self, request=None):
        if not request:
            return self.tier_rates.get("free", "100/hour")

        tier = self.get_user_tier(request)
        return self.tier_rates.get(tier, "100/hour")

    def allow_request(self, request, view):
        if self.get_user_tier(request) == "enterprise":
            return True

        self.scope = getattr(view, "throttle_scope", "user")
        self.rate = self.get_rate(request)
        self.num_requests, self.duration = self.parse_rate(self.rate)

        cache_key = self.get_cache_key(request, view)
        history = cache.get(cache_key, [])
        now = time.time()

        # Remove old entries
        history = [timestamp for timestamp in history if timestamp > now - self.duration]

        if len(history) >= self.num_requests:
            return False

        history.append(now)
        cache.set(cache_key, history, self.duration)
        return True

    def wait(self):
        """Return recommended wait time."""
        if hasattr(self, "history") and self.history:
            oldest = self.history[0]
            now = time.time()
            return self.duration - (now - oldest)
        return None


class BurstRateThrottle(SimpleRateThrottle):
    """Handle burst traffic with token bucket algorithm."""

    scope = "burst"

    def __init__(self):
        super().__init__()
        self.burst_size = 10
        self.refill_rate = 1  # tokens per second

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.id
        else:
            ident = self.get_ident(request)

        return f"burst_{self.scope}_{ident}"

    def allow_request(self, request, view):
        cache_key = self.get_cache_key(request, view)
        bucket_key = f"{cache_key}_bucket"
        last_refill_key = f"{cache_key}_refill"

        # Get current bucket state
        tokens = cache.get(bucket_key, self.burst_size)
        last_refill = cache.get(last_refill_key, time.time())

        now = time.time()
        elapsed = now - last_refill

        # Refill tokens
        tokens = min(self.burst_size, tokens + elapsed * self.refill_rate)

        if tokens >= 1:
            tokens -= 1
            cache.set(bucket_key, tokens, 3600)
            cache.set(last_refill_key, now, 3600)
            return True

        return False


class EndpointThrottle(SimpleRateThrottle):
    """Per-endpoint customizable throttling."""

    endpoint_rates = {
        "auth.login": "5/hour",
        "auth.register": "10/hour",
        "auth.forgot_password": "3/hour",
        "trials.create": "20/hour",
        "analytics.track_event": "1000/hour",
        "subscriptions.create": "10/hour",
    }

    def get_cache_key(self, request, view):
        endpoint = f"{view.__module__.split('.')[-2]}.{view.__class__.__name__.lower()}"

        if request.user.is_authenticated:
            ident = request.user.id
        else:
            ident = self.get_ident(request)

        return f"endpoint_{endpoint}_{ident}"

    def get_rate(self):
        view_name = getattr(self, "view_name", None)
        if view_name and view_name in self.endpoint_rates:
            return self.endpoint_rates[view_name]
        return "100/hour"


class IPBasedThrottle(BaseThrottle):
    """Advanced IP-based throttling with subnet support."""

    def __init__(self):
        self.rate = "60/hour"
        self.num_requests, self.duration = self.parse_rate(self.rate)
        self.suspicious_ips = cache.get("suspicious_ips", set())

    def get_ident(self, request):
        """Enhanced IP detection."""
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        remote_addr = request.META.get("REMOTE_ADDR")

        if xff:
            ip = xff.split(",")[0].strip()
        else:
            ip = remote_addr

        # Check for suspicious patterns
        if self.is_suspicious_ip(ip):
            self.rate = "10/hour"
            self.num_requests, self.duration = self.parse_rate(self.rate)

        return ip

    def is_suspicious_ip(self, ip):
        # Check against known VPN/Proxy ranges
        vpn_ranges = getattr(settings, "VPN_IP_RANGES", [])
        for range_start, range_end in vpn_ranges:
            if self.ip_in_range(ip, range_start, range_end):
                return True
        return ip in self.suspicious_ips

    def ip_in_range(self, ip, start, end):
        # Simple IP range check
        return start <= ip <= end

    def allow_request(self, request, view):
        ident = self.get_ident(request)
        cache_key = f"ip_throttle_{ident}"

        history = cache.get(cache_key, [])
        now = time.time()

        # Clean old entries
        history = [timestamp for timestamp in history if timestamp > now - self.duration]

        if len(history) >= self.num_requests:
            # Mark as suspicious if hitting limits frequently
            if len(history) >= self.num_requests * 2:
                self.suspicious_ips.add(ident)
                cache.set("suspicious_ips", self.suspicious_ips, 86400)
            return False

        history.append(now)
        cache.set(cache_key, history, self.duration)
        return True


class CompositeThrottle(BaseThrottle):
    """Combine multiple throttle strategies."""

    throttle_classes = [
        TierBasedRateThrottle,
        IPBasedThrottle,
        EndpointThrottle,
    ]

    def allow_request(self, request, view):
        for throttle_class in self.throttle_classes:
            throttle = throttle_class()
            if not throttle.allow_request(request, view):
                self.throttle = throttle
                return False
        return True

    def wait(self):
        if hasattr(self, "throttle"):
            return self.throttle.wait()
        return None
