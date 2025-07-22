"""DRF serializers for API."""
from rest_framework import serializers

from .models import Invoice, PaymentMethod, Subscription


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "provider", "card_last4", "card_brand", "is_default", "created_at"]
        read_only_fields = ["id", "created_at"]


class SubscriptionSerializer(serializers.ModelSerializer):
    trial_name = serializers.CharField(source="trial.title", read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "trial",
            "trial_name",
            "status",
            "amount",
            "currency",
            "current_period_start",
            "current_period_end",
            "cancel_at_period_end",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    trial_name = serializers.CharField(source="subscription.trial.title", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "trial_name",
            "status",
            "amount_paid",
            "amount_due",
            "currency",
            "period_start",
            "period_end",
            "invoice_pdf",
            "created_at",
        ]
