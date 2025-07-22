"""DRF serializers for API."""
from rest_framework import serializers

from .models import ConsentType, PolicyVersion, UserConsent


class ConsentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentType
        fields = ["id", "name", "category", "description", "is_required"]


class UserConsentSerializer(serializers.ModelSerializer):
    consent_type_name = serializers.CharField(source="consent_type.name", read_only=True)

    class Meta:
        model = UserConsent
        fields = ["id", "consent_type", "consent_type_name", "given", "version", "created_at"]


class PolicyVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyVersion
        fields = ["id", "policy_type", "version", "content", "summary_of_changes", "effective_date"]


class ConsentUpdateSerializer(serializers.Serializer):
    consents = serializers.DictField(child=serializers.BooleanField())
