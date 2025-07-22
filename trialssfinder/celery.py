import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trialssfinder.settings")

app = Celery("trialssfinder")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Task routing
app.conf.task_routes = {
    "apps.notifications.tasks.*": {"queue": "notifications"},
    "apps.analytics.tasks.*": {"queue": "analytics"},
    "apps.trials.tasks.*": {"queue": "default"},
}

# Task priorities
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1
