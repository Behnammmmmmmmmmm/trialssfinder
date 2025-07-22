"""Database models."""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("user", "User"),
        ("company", "Company"),
        ("admin", "Admin"),
    )

    TIER_CHOICES = (
        ("free", "Free"),
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("enterprise", "Enterprise"),
    )

    user_type: models.CharField = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default="user")
    email_verified: models.BooleanField = models.BooleanField(default=False)
    verification_token: models.CharField = models.CharField(max_length=255, blank=True)
    reset_token: models.CharField = models.CharField(max_length=255, blank=True)
    tier: models.CharField = models.CharField(max_length=20, choices=TIER_CHOICES, default="free")
    language_preference: models.CharField = models.CharField(
        max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name=_("Language Preference")
    )

    class Meta:
        db_table = "users"
