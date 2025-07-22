"""Celery background tasks."""
import csv
import io

from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
User = get_user_model()


@shared_task
def generate_admin_report(admin_id, report_type, params):
    try:
        admin = User.objects.get(id=admin_id)

        if report_type == "user_activity":
            report_data = generate_user_activity_report(params)
        elif report_type == "revenue":
            report_data = generate_revenue_report(params)
        elif report_type == "trial_performance":
            report_data = generate_trial_performance_report(params)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=report_data[0].keys())
        writer.writeheader()
        writer.writerows(report_data)

        # Send email with attachment
        send_mail(
            f"Admin Report: {report_type}",
            f"Your requested {report_type} report is attached.",
            "reports@trialssfinder.com",
            [admin.email],
            fail_silently=False,
            # Add attachment logic here
        )

        logger.info(f"Report {report_type} generated for admin {admin_id}")
        return {"status": "success", "rows": len(report_data)}

    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise


@shared_task
def bulk_process_trials(trial_ids, action):
    from apps.notifications.tasks import bulk_create_notifications
    from apps.trials.models import Trial

    if action == "approve":
        trials = Trial.objects.filter(id__in=trial_ids)

        # Group by industry for notifications
        industry_users = {}
        for trial in trials:
            if trial.industry_id not in industry_users:
                from apps.trials.models import UserIndustry

                industry_users[trial.industry_id] = list(
                    UserIndustry.objects.filter(industry_id=trial.industry_id).values_list("user_id", flat=True)
                )

            # Send notifications
            if industry_users[trial.industry_id]:
                message = f'New trial "{trial.title}" is now available!'
                bulk_create_notifications.delay(industry_users[trial.industry_id], message)

    return {"processed": len(trial_ids)}


def generate_user_activity_report(params):
    # Implementation here
    pass


def generate_revenue_report(params):
    # Implementation here
    pass


def generate_trial_performance_report(params):
    # Implementation here
    pass
