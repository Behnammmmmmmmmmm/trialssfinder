"""Database models."""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AdminAction(models.Model):
    ACTION_TYPES = (
        ("user_banned", "User Banned"),
        ("user_unbanned", "User Unbanned"),
        ("trial_approved", "Trial Approved"),
        ("trial_rejected", "Trial Rejected"),
        ("trial_featured", "Trial Featured"),
        ("system_config", "System Configuration"),
        ("bulk_action", "Bulk Action"),
    )

    admin: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type: models.CharField = models.CharField(max_length=50, choices=ACTION_TYPES)
    target_model: models.CharField = models.CharField(max_length=50)
    target_id: models.IntegerField = models.IntegerField(null=True, blank=True)
    details: models.JSONField = models.JSONField(default=dict)
    timestamp: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} - {self.action_type} - {self.timestamp}"

    class Meta:
        db_table = "admin_actions"
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["admin", "-timestamp"]),
            models.Index(fields=["action_type", "-timestamp"]),
        ]


class SystemConfig(models.Model):
    key: models.CharField = models.CharField(max_length=100, unique=True)
    value: models.JSONField = models.JSONField()
    description: models.TextField = models.TextField(blank=True)
    updated_by: models.ForeignKey = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        db_table = "system_configs"
