"""Database models."""
from django.db import models

from apps.authentication.models import User


class Notification(models.Model):
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message: models.TextField = models.TextField()
    is_read: models.BooleanField = models.BooleanField(default=False)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"


class Meta:
    db_table = "notifications"


class ContactMessage(models.Model):
    name: models.CharField = models.CharField(max_length=100)
    email: models.EmailField = models.EmailField()
    subject: models.CharField = models.CharField(max_length=200)
    message: models.TextField = models.TextField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} from {self.email}"


class Meta:
    db_table = "contact_messages"
