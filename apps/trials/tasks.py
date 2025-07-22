"""Celery background tasks."""
from django.db import transaction

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import Trial

logger = get_task_logger(__name__)


@shared_task(bind=True)
def process_trial_approval(self, trial_id):
    try:
        with transaction.atomic():
            trial = Trial.objects.select_for_update().get(id=trial_id)

            if trial.status != "under_review":
                return {"status": "skipped", "reason": "Invalid status"}

            # Trigger notification task
            from apps.notifications.tasks import bulk_create_notifications

            from .models import UserIndustry

            user_ids = list(UserIndustry.objects.filter(industry=trial.industry).values_list("user_id", flat=True))

            if user_ids:
                message = f'New trial "{trial.title}" in {trial.industry.name} is now available!'
                bulk_create_notifications.delay(user_ids, message)

            logger.info(f"Trial {trial_id} approval processed")
            return {"status": "success", "notified_users": len(user_ids)}

    except Trial.DoesNotExist:
        logger.error(f"Trial {trial_id} not found")
        raise


@shared_task
def expire_old_trials():
    from django.utils import timezone

    expired = Trial.objects.filter(end_date__lt=timezone.now().date(), status="approved").update(status="expired")

    return {"expired": expired}
