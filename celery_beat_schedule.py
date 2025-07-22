import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask

# Daily cleanup at 2 AM
daily_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="0",
    hour="2",
)

PeriodicTask.objects.get_or_create(
    crontab=daily_schedule,
    name="Cleanup old notifications",
    task="apps.notifications.tasks.cleanup_old_notifications",
)

PeriodicTask.objects.get_or_create(
    crontab=daily_schedule,
    name="Expire old trials",
    task="apps.trials.tasks.expire_old_trials",
)

# Daily metrics aggregation at 1 AM
metrics_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="0",
    hour="1",
)

PeriodicTask.objects.get_or_create(
    crontab=metrics_schedule,
    name="Aggregate daily metrics",
    task="apps.analytics.tasks.aggregate_daily_metrics",
)
