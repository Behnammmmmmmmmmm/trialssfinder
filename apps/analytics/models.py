"""Database models."""
from django.db import models

from apps.authentication.models import User
from apps.trials.models import Trial


class AnalyticsEvent(models.Model):
    EVENT_TYPES = (
        ("trial_view", "Trial View"),
        ("trial_start", "Trial Start"),
    )

    event_type: models.CharField = models.CharField(max_length=20, choices=EVENT_TYPES)
    trial: models.ForeignKey = models.ForeignKey(Trial, on_delete=models.CASCADE, related_name="analytics_events")
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.trial.title} - {self.timestamp}"

    class Meta:
        db_table = "analytics_events"
