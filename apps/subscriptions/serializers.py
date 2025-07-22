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
        fields = ["id", "trial", "trial_name", "amount", "status", "created_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["id", "amount", "created_at"]
