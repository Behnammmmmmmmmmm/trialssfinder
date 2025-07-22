from django.utils import timezone

"""Celery background tasks."""
from datetime import timedelta

from django.db.models import Count, Q

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import AnalyticsEvent

logger = get_task_logger(__name__)


@shared_task
def generate_trial_report(trial_id, period_days=30):
    try:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period_days)

        events = AnalyticsEvent.objects.filter(trial_id=trial_id, timestamp__range=[start_date, end_date])

        report = {
            "trial_id": trial_id,
            "period": period_days,
            "total_views": events.filter(event_type="trial_view").count(),
            "total_clicks": events.filter(event_type="trial_start").count(),
            "unique_users": events.values("user").distinct().count(),
            "generated_at": timezone.now().isoformat(),
        }

        logger.info(f"Report generated for trial {trial_id}")
        return report

    except Exception as exc:
        logger.error(f"Report generation failed: {exc}")
        raise


@shared_task
def aggregate_daily_metrics():
    yesterday = timezone.now().date() - timedelta(days=1)

    metrics = (
        AnalyticsEvent.objects.filter(timestamp__date=yesterday)
        .values("trial_id")
        .annotate(
            views=Count("id", filter=Q(event_type="trial_view")), clicks=Count("id", filter=Q(event_type="trial_start"))
        )
    )

    return list(metrics)
