"""Celery background tasks."""
from django.core.mail import send_mail
from django.db import transaction

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import Notification

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, user_id, subject, message):
    try:
        from apps.authentication.models import User

        user = User.objects.get(id=user_id)

        send_mail(
            subject,
            message,
            "noreply@trialssfinder.com",
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Email sent to {user.email}")
        return {"status": "success", "email": user.email}

    except Exception as exc:
        logger.error(f"Email sending failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task
def bulk_create_notifications(user_ids, message):
    with transaction.atomic():
        notifications = [Notification(user_id=user_id, message=message) for user_id in user_ids]
        Notification.objects.bulk_create(notifications)

    return {"created": len(notifications)}


@shared_task
def cleanup_old_notifications():
    from datetime import timedelta

    from django.utils import timezone

    cutoff = timezone.now() - timedelta(days=30)
    deleted = Notification.objects.filter(created_at__lt=cutoff, is_read=True).delete()

    return {"deleted": deleted[0]}
