"""Celery background tasks."""
import json
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from celery import shared_task
from celery.utils.log import get_task_logger

from apps.analytics.models import AnalyticsEvent
from apps.notifications.models import Notification
from apps.trials.models import FavoriteTrial, UserIndustry

from .models import DataDeletionRequest, DataRetentionPolicy, UserConsent

logger = get_task_logger(__name__)


@shared_task
def process_deletion_request(request_id):
    """Process GDPR deletion request"""
    try:
        request = DataDeletionRequest.objects.get(id=request_id)
        user = request.user

        if not user:
            logger.error(f"No user found for deletion request {request_id}")
            return

        with transaction.atomic():
            # Delete user data in order of dependencies

            # Delete analytics events
            AnalyticsEvent.objects.filter(user=user).delete()

            # Delete notifications
            Notification.objects.filter(user=user).delete()

            # Delete favorites
            FavoriteTrial.objects.filter(user=user).delete()

            # Delete industry follows
            UserIndustry.objects.filter(user=user).delete()

            # Delete consents
            UserConsent.objects.filter(user=user).delete()

            # Delete trials if company
            if hasattr(user, "company"):
                user.company.trials.all().delete()
                user.company.delete()

            # Finally delete the user
            user_id = user.id
            user.delete()

            # Mark request as completed
            request.status = "completed"
            request.processed_at = timezone.now()
            request.save()

            logger.info(f"Deletion request {request_id} completed for user {user_id}")

    except DataDeletionRequest.DoesNotExist:
        logger.error(f"Deletion request {request_id} not found")
    except Exception as e:
        logger.error(f"Deletion request {request_id} failed: {str(e)}")
        request.status = "rejected"
        request.save()
        raise


@shared_task
def export_user_data(request_id):
    """Export user data for GDPR portability."""
    try:
        request = DataDeletionRequest.objects.get(id=request_id)
        user = request.user

        if not user:
            logger.error(f"No user found for export request {request_id}")
            return

        # Collect all user data
        data = {
            "profile": {
                "username": user.username,
                "email": user.email,
                "user_type": user.user_type,
                "email_verified": user.email_verified,
                "tier": user.tier,
                "language_preference": user.language_preference,
                "date_joined": user.date_joined.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "company": None,
            "trials": [],
            "favorites": [],
            "followed_industries": [],
            "notifications": [],
            "consents": [],
            "analytics_events": [],
        }

        # Company data
        if hasattr(user, "company"):
            company = user.company
            data["company"] = {
                "name": company.name,
                "address": company.address,
                "phone": company.phone,
                "website": company.website,
                "created_at": company.created_at.isoformat(),
            }

            # Company trials
            for trial in company.trials.all():
                data["trials"].append(
                    {
                        "title": trial.title,
                        "description": trial.description,
                        "industry": trial.industry.name,
                        "location": trial.location,
                        "start_date": trial.start_date.isoformat(),
                        "end_date": trial.end_date.isoformat(),
                        "status": trial.status,
                        "is_featured": trial.is_featured,
                        "created_at": trial.created_at.isoformat(),
                    }
                )

        # Favorites
        for favorite in FavoriteTrial.objects.filter(user=user).select_related("trial"):
            data["favorites"].append(
                {
                    "trial_title": favorite.trial.title,
                    "favorited_at": favorite.created_at.isoformat(),
                }
            )

        # Followed industries
        for follow in UserIndustry.objects.filter(user=user).select_related("industry"):
            data["followed_industries"].append(
                {
                    "industry": follow.industry.name,
                    "followed_at": follow.created_at.isoformat(),
                }
            )

        # Notifications
        for notification in Notification.objects.filter(user=user)[:100]:  # Limit to recent 100
            data["notifications"].append(
                {
                    "message": notification.message,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                }
            )

        # Consents
        for consent in UserConsent.objects.filter(user=user).select_related("consent_type"):
            data["consents"].append(
                {
                    "type": consent.consent_type.name,
                    "given": consent.given,
                    "version": consent.version,
                    "created_at": consent.created_at.isoformat(),
                }
            )

        # Analytics events (limited)
        for event in AnalyticsEvent.objects.filter(user=user).order_by("-timestamp")[:100]:
            data["analytics_events"].append(
                {
                    "event_type": event.event_type,
                    "trial_id": event.trial_id,
                    "timestamp": event.timestamp.isoformat(),
                }
            )

        # Convert to JSON
        json_data = json.dumps(data, indent=2)

        # Send email with data
        from django.core.mail import EmailMessage

        email = EmailMessage(
            subject="Your TrialsFinder Data Export",
            body="Please find attached your requested data export.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach("trialssfinder_data_export.json", json_data, "application/json")
        email.send()

        # Mark request as completed
        request.status = "completed"
        request.processed_at = timezone.now()
        request.save()

        logger.info(f"Data export completed for user {user.id}")

    except DataDeletionRequest.DoesNotExist:
        logger.error(f"Export request {request_id} not found")
    except Exception as e:
        logger.error(f"Data export failed: {str(e)}")
        request.status = "rejected"
        request.save()
        raise


@shared_task
def cleanup_old_data():
    """Clean up old data based on retention policies."""
    policies = DataRetentionPolicy.objects.filter(is_active=True)

    for policy in policies:
        cutoff_date = timezone.now() - timedelta(days=policy.retention_days)

        if policy.data_type == "analytics_events":
            deleted = AnalyticsEvent.objects.filter(timestamp__lt=cutoff_date).delete()
            logger.info(f"Deleted {deleted[0]} old analytics events")
        elif policy.data_type == "notifications":
            deleted = Notification.objects.filter(created_at__lt=cutoff_date, is_read=True).delete()
            logger.info(f"Deleted {deleted[0]} old read notifications")
        elif policy.data_type == "user_consents":
            # Keep only the most recent consent for each type per user
            # This is more complex and would need careful implementation
            pass

    return {"status": "completed"}
