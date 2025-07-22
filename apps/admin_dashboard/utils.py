"""Module implementation."""
from datetime import datetime, timedelta

from django.core.cache import cache


def get_cached_or_compute(cache_key, compute_func, timeout=300):
    """Helper to get cached data or compute if missing"""
    data = cache.get(cache_key)
    if data is None:
        data = compute_func()
        cache.set(cache_key, data, timeout)
    return data


def calculate_growth_rate(current, previous):
    """Calculate percentage growth rate"""
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100


def get_date_range(period):
    """Get start and end dates for a period"""
    now = datetime.now()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "week":
        start = now - timedelta(days=7)
        end = now
    elif period == "month":
        start = now - timedelta(days=30)
        end = now
    elif period == "year":
        start = now - timedelta(days=365)
        end = now
    else:
        raise ValueError(f"Invalid period: {period}")

    return start, end
