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
    company: models.ForeignKey = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="payment_methods_new"
    )
    provider: models.CharField = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="stripe")
    provider_customer_id: models.CharField = models.CharField(max_length=255, blank=True)
    provider_payment_method_id: models.CharField = models.CharField(max_length=255, blank=True)
    card_last4: models.CharField = models.CharField(max_length=4, blank=True)
    card_brand: models.CharField = models.CharField(max_length=20, blank=True)
    is_default: models.BooleanField = models.BooleanField(default=False)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.card_brand} ****{self.card_last4}"


class Meta:
    db_table = "payments_payment_methods"
    indexes = [
        models.Index(fields=["company", "-created_at"]),
    ]


class Subscription(models.Model):
    STATUS_CHOICES = (
        ("trialing", "Trialing"),
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("canceled", "Canceled"),
        ("unpaid", "Unpaid"),
    )

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company: models.ForeignKey = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="payment_subscriptions"
    )
    trial: models.ForeignKey = models.ForeignKey(Trial, on_delete=models.CASCADE, related_name="payment_subscriptions")
    payment_method: models.ForeignKey = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    provider_subscription_id: models.CharField = models.CharField(max_length=255, blank=True)
    status: models.CharField = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trialing")
    amount: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    currency: models.CharField = models.CharField(max_length=3, default="USD")
    current_period_start: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    current_period_end: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end: models.BooleanField = models.BooleanField(default=False)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.trial.title}"


class Meta:
    db_table = "payments_subscriptions"
    indexes = [
        models.Index(fields=["company", "-created_at"]),
        models.Index(fields=["status", "current_period_end"]),
    ]


class Invoice(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("open", "Open"),
        ("paid", "Paid"),
        ("void", "Void"),
        ("uncollectible", "Uncollectible"),
    )

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription: models.ForeignKey = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices")
    provider_invoice_id: models.CharField = models.CharField(max_length=255, blank=True)
    invoice_number: models.CharField = models.CharField(max_length=50, blank=True)
    status: models.CharField = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    amount_due: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency: models.CharField = models.CharField(max_length=3, default="USD")
    period_start: models.DateTimeField = models.DateTimeField()
    period_end: models.DateTimeField = models.DateTimeField()
    invoice_pdf: models.URLField = models.URLField(blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number or self.id}"


class Meta:
    db_table = "payments_invoices"
    indexes = [
        models.Index(fields=["subscription", "-created_at"]),
    ]


class PaymentEvent(models.Model):
    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider: models.CharField = models.CharField(max_length=20, default="stripe")
    event_type: models.CharField = models.CharField(max_length=50)
    provider_event_id: models.CharField = models.CharField(max_length=255, unique=True)
    data: models.JSONField = models.JSONField()
    processed: models.BooleanField = models.BooleanField(default=False)
    error: models.TextField = models.TextField(blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.provider_event_id}"


class Meta:
    db_table = "payment_events"
    indexes = [
        models.Index(fields=["provider", "event_type", "-created_at"]),
        models.Index(fields=["processed", "created_at"]),
    ]
