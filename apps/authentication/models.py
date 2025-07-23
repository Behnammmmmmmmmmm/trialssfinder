from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('company', 'Company'),
        ('admin', 'Admin'),
    ]
    
    TIER_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    # Override username field to make it optional
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True
    )
    
    # Make email required and unique
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True)
    reset_token = models.CharField(max_length=255, blank=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='free')
    language_preference = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        verbose_name=_('Language Preference')
    )
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove email from REQUIRED_FIELDS since it's the USERNAME_FIELD
    
    def save(self, *args, **kwargs):
        # Auto-generate username from email if not provided
        if not self.username:
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'users'