"""Database models."""
import uuid

from django.db import models

from apps.companies.models import Company
from apps.trials.models import Trial


class PaymentMethod(models.Model):
    PROVIDER_CHOICES = (
        ("stripe", "Stripe"),
        ("paypal", "PayPal"),
    )

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company: models.ForeignKey = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="payment_methods")
    provider: models.CharField = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="stripe")
    provider_customer_id: models.CharField = models.CharField(max_length=255, blank=True)
    provider_payment_method_id: models.CharField = models.CharField(max_length=255, blank=True)
    card_last4: models.CharField = models.CharField(max_length=4, blank=True)
    card_brand: models.CharField = models.CharField(max_length=20, blank=True)
    is_default: models.BooleanField = models.BooleanField(default=False)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.provider} ****{self.card_last4}"

    class Meta:
        db_table = "payment_methods"
        indexes = [
            models.Index(fields=["company", "-created_at"]),
        ]


class Subscription(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("canceled", "Canceled"),
    )

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company: models.ForeignKey = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="subscriptions")
    trial: models.ForeignKey = models.ForeignKey(Trial, on_delete=models.CASCADE)
    payment_method: models.ForeignKey = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    status: models.CharField = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.trial.title} - {self.status}"

    class Meta:
        db_table = "subscriptions"
        indexes = [
            models.Index(fields=["company", "-created_at"]),
        ]


class Invoice(models.Model):
    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription: models.ForeignKey = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices")
    amount: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for {self.subscription}"

    class Meta:
        db_table = "invoices"
