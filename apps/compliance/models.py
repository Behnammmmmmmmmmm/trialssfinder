"""Database models."""
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ConsentType(models.Model):
    """Types of consent that can be tracked"""

    CONSENT_CATEGORIES = (
        ("necessary", _("Necessary")),
        ("functional", _("Functional")),
        ("analytics", _("Analytics")),
        ("marketing", _("Marketing")),
    )

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name: models.CharField = models.CharField(max_length=100, unique=True)
    category: models.CharField = models.CharField(max_length=20, choices=CONSENT_CATEGORIES)
    description: models.TextField = models.TextField()
    is_required: models.BooleanField = models.BooleanField(default=False)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        db_table = "consent_types"


class UserConsent(models.Model):
    """Track user consent for various purposes."""

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consents")
    consent_type: models.ForeignKey = models.ForeignKey(ConsentType, on_delete=models.PROTECT)
    version: models.CharField = models.CharField(max_length=20)
    given: models.BooleanField = models.BooleanField(default=False)
    ip_address: models.GenericIPAddressField = models.GenericIPAddressField()
    user_agent: models.TextField = models.TextField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    expires_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.consent_type.name} - {self.given}"

    class Meta:
        db_table = "user_consents"
        indexes = [
            models.Index(fields=["user", "consent_type", "-created_at"]),
        ]


class PolicyVersion(models.Model):
    """Track versions of legal documents."""

    POLICY_TYPES = (
        ("terms", _("Terms of Service")),
        ("privacy", _("Privacy Policy")),
        ("cookies", _("Cookie Policy")),
    )

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_type: models.CharField = models.CharField(max_length=20, choices=POLICY_TYPES)
    version: models.CharField = models.CharField(max_length=20)
    content: models.TextField = models.TextField()
    summary_of_changes: models.TextField = models.TextField(blank=True)
    effective_date: models.DateTimeField = models.DateTimeField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    created_by: models.ForeignKey = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.policy_type} v{self.version}"

    class Meta:
        db_table = "policy_versions"
        unique_together = ["policy_type", "version"]
        indexes = [
            models.Index(fields=["policy_type", "-effective_date"]),
        ]


class UserPolicyAcceptance(models.Model):
    """Track user acceptance of policies."""

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE, related_name="policy_acceptances")
    policy_version: models.ForeignKey = models.ForeignKey(PolicyVersion, on_delete=models.PROTECT)
    accepted_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    ip_address: models.GenericIPAddressField = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.user.username} - {self.policy_version}"

    class Meta:
        db_table = "user_policy_acceptances"
        unique_together = ["user", "policy_version"]


class DataRetentionPolicy(models.Model):
    """Define data retention policies."""

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_type: models.CharField = models.CharField(max_length=100, unique=True)
    retention_days: models.IntegerField = models.IntegerField()
    description: models.TextField = models.TextField()
    is_active: models.BooleanField = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.data_type} - {self.retention_days} days"

    class Meta:
        db_table = "data_retention_policies"


class DataDeletionRequest(models.Model):
    """Track GDPR deletion requests."""

    STATUS_CHOICES = (
        ("pending", _("Pending")),
        ("processing", _("Processing")),
        ("completed", _("Completed")),
        ("rejected", _("Rejected")),
    )

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="deletion_requests"
    )
    request_type: models.CharField = models.CharField(
        max_length=20, choices=[("deletion", "Deletion"), ("portability", "Portability")]
    )
    status: models.CharField = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reason: models.TextField = models.TextField(blank=True)
    requested_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    processed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    processed_by: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="processed_deletions"
    )
    verification_token: models.CharField = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.request_type} - {self.user.username if self.user else 'Unknown'} - {self.status}"

    class Meta:
        db_table = "data_deletion_requests"
        indexes = [
            models.Index(fields=["status", "requested_at"]),
        ]
