"""Celery background tasks."""
from django.core.cache import cache

from celery import shared_task
from celery.utils.log import get_task_logger

from apps.trials.models import Trial

from .analytics import SearchAnalytics
from .search_backends import ElasticsearchBackend

logger = get_task_logger(__name__)


@shared_task
def index_trial(trial_id: int):
    """Index a single trial"""
    try:
        trial = Trial.objects.get(id=trial_id)
        backend = ElasticsearchBackend()

        trial_data = {
            "id": trial.id,
            "title": trial.title,
            "description": trial.description,
            "industry": trial.industry.name,
            "industry_id": trial.industry.id,
            "location": trial.location,
            "company_name": trial.company.name,
            "company_id": trial.company.id,
            "start_date": trial.start_date.isoformat(),
            "end_date": trial.end_date.isoformat(),
            "is_featured": trial.is_featured,
            "status": trial.status,
            "created_at": trial.created_at.isoformat(),
        }

        backend.index_trial(trial_data)
        logger.info(f"Indexed trial {trial_id}")

    except Trial.DoesNotExist:
        logger.error(f"Trial {trial_id} not found")


@shared_task
def reindex_all_trials():
    """Reindex all approved trials."""
    backend = ElasticsearchBackend()
    backend.create_index()

    trials = Trial.objects.filter(status="approved").select_related("industry", "company")

    trial_data = []
    for trial in trials:
        trial_data.append(
            {
                "id": trial.id,
                "title": trial.title,
                "description": trial.description,
                "industry": trial.industry.name,
                "industry_id": trial.industry.id,
                "location": trial.location,
                "company_name": trial.company.name,
                "company_id": trial.company.id,
                "start_date": trial.start_date.isoformat(),
                "end_date": trial.end_date.isoformat(),
                "is_featured": trial.is_featured,
                "status": trial.status,
                "created_at": trial.created_at.isoformat(),
            }
        )

    backend.bulk_index_trials(trial_data)
    logger.info(f"Reindexed {len(trial_data)} trials")


@shared_task
def update_search_analytics():
    """Update search analytics cache."""
    analytics = SearchAnalytics()

    # Popular searches
    popular = analytics.get_popular_searches(limit=100)
    cache.set("search:popular_queries", popular, 3600)

    # Zero result queries
    zero_results = analytics.get_zero_result_queries(limit=50)
    cache.set("search:zero_results", zero_results, 3600)

    logger.info("Updated search analytics cache")
