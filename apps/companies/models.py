"""Database models."""
from django.db import models

from apps.authentication.models import User


class Company(models.Model):
    user: models.OneToOneField = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    name: models.CharField = models.CharField(max_length=255)
    address: models.TextField = models.TextField()
    phone: models.CharField = models.CharField(max_length=20)
    website: models.URLField = models.URLField(blank=True)
    stripe_customer_id: models.CharField = models.CharField(max_length=255, blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "companies"
        verbose_name_plural = "Companies"
