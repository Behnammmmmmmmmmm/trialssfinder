"""Cache warming module for performance optimization."""
import logging

from django.core.cache import cache
from django.db.models import Count, Q

from celery import shared_task

from apps.trials.models import Industry, Trial

logger = logging.getLogger("trialssfinder.cache")


@shared_task
def warm_cache():
    """Warm critical caches."""
    try:
        # Warm featured trials
        featured_trials = Trial.objects.filter(
            status="approved", 
            is_featured=True
        ).select_related(
            "company", 
            "industry"
        )
        
        cache.set("trials:featured", list(featured_trials), 3600)
        
        # Warm industries with trial counts
        industries = Industry.objects.annotate(
            trial_count=Count("trial", filter=Q(trial__status="approved"))
        )
        cache.set("industries:with_counts", list(industries), 3600)
        
        # Warm popular trials (by analytics)
        popular_trials = (
            Trial.objects.filter(status="approved")
            .annotate(
                view_count=Count(
                    "analytics_events", 
                    filter=Q(analytics_events__event_type="trial_view")
                )
            )
            .order_by("-view_count")[:20]
        )
        
        cache.set("trials:popular", list(popular_trials), 1800)
        
        logger.info("Cache warming completed")
        return {"status": "success", "caches_warmed": 3}
        
    except Exception as e:
        logger.error(f"Cache warming failed: {str(e)}")
        return {"status": "failed", "error": str(e)}


@shared_task
def invalidate_stale_caches():
    """Invalidate potentially stale caches."""
    from django.core.cache import cache
    
    patterns = [
        "api_response:*",  # Clear old API responses
        "trials:list:*",   # Clear paginated lists
    ]
    
    total_cleared = 0
    
    # Since Django's default cache doesn't support pattern deletion,
    # we'll implement a simple version
    if hasattr(cache, '_cache'):
        # For LocMemCache
        for key in list(cache._cache.keys()):
            for pattern in patterns:
                if pattern.endswith('*') and key.startswith(pattern[:-1]):
                    cache.delete(key)
                    total_cleared += 1
    
    logger.info(f"Cleared {total_cleared} stale cache entries")
    return {"cleared": total_cleared}