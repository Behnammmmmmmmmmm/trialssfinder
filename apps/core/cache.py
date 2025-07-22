"""Module implementation."""
import hashlib
import json
from functools import wraps

from django.core.cache import cache


def make_cache_key(prefix, *args, **kwargs):
    """Generate a cache key from prefix and arguments"""
    key_parts = [prefix] + [str(arg) for arg in args]
    if kwargs:
        # Sort kwargs for consistent keys
        sorted_kwargs = json.dumps(kwargs, sort_keys=True)
        key_parts.append(hashlib.md5(sorted_kwargs.encode(), usedforsecurity=False).hexdigest()[:8])
    return ":".join(key_parts)


def cache_result(key_prefix, timeout=300):
    """Simple decorator for caching function results."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = make_cache_key(key_prefix, *args, **kwargs)

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, timeout)

            return result

        return wrapper

    return decorator


def invalidate_pattern(pattern):
    """Delete all cache keys matching a pattern."""
    # Check if the cache backend supports delete_pattern natively
    if hasattr(cache, '_cache') and hasattr(cache._cache, 'delete_pattern'):
        # Redis backend
        return cache._cache.delete_pattern(f"*{pattern}*")
    elif hasattr(cache, '_cache') and hasattr(cache._cache, 'keys'):
        # LocMemCache backend - manual deletion
        deleted = 0
        try:
            for key in list(cache._cache.keys()):
                if pattern in key:
                    cache.delete(key)
                    deleted += 1
        except:
            pass
        return deleted
    else:
        # Unsupported backend - just return 0
        return 0


def invalidate_user_cache(user_id):
    """Invalidate all caches for a specific user."""
    patterns = [
        f"user:{user_id}",
        f"favorites:{user_id}",
        f"notifications:{user_id}",
    ]
    for pattern in patterns:
        invalidate_pattern(pattern)


def invalidate_trial_cache(trial_id):
    """Invalidate all caches for a specific trial."""
    patterns = [
        f"trial:{trial_id}",
        f"trials:",
    ]
    for pattern in patterns:
        invalidate_pattern(pattern)


class CacheManager:
    """Cache manager class for centralized cache operations."""

    def __init__(self):
        self.cache = cache

    def get(self, key, default=None):
        """Get value from cache."""
        return self.cache.get(key, default)

    def set(self, key, value, timeout=300):
        """Set value in cache."""
        return self.cache.set(key, value, timeout)

    def delete(self, key):
        """Delete key from cache."""
        return self.cache.delete(key)

    def invalidate_pattern(self, pattern):
        """Invalidate all keys matching pattern."""
        return invalidate_pattern(pattern)

    def invalidate_user_cache(self, user_id):
        """Invalidate all caches for a user."""
        return invalidate_user_cache(user_id)

    def invalidate_trial_cache(self, trial_id):
        """Invalidate all caches for a trial."""
        return invalidate_trial_cache(trial_id)

    def cache_page_response(self, timeout="short"):
        """Decorator for caching page responses."""
        timeouts = {
            "short": 300,  # 5 minutes
            "medium": 1800,  # 30 minutes
            "long": 3600,  # 1 hour
        }
        actual_timeout = timeouts.get(timeout, timeout if isinstance(timeout, int) else 300)

        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                # Generate cache key based on request
                cache_key = make_cache_key("page_response", request.path, request.GET.dict() if request.GET else {})

                # Try to get from cache
                cached = self.get(cache_key)
                if cached is not None:
                    return cached

                # Call function and cache result
                response = func(request, *args, **kwargs)
                if hasattr(response, "status_code") and response.status_code == 200:
                    self.set(cache_key, response, actual_timeout)

                return response

            return wrapper

        return decorator


# Create global cache manager instance
cache_manager = CacheManager()


# Monkey-patch delete_pattern method for cache backends that don't have it
if not hasattr(cache, 'delete_pattern'):
    cache.delete_pattern = lambda pattern: invalidate_pattern(pattern.replace('*', ''))