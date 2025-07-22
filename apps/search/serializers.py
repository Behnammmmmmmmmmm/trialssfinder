"""DRF serializers for API."""
from rest_framework import serializers

from apps.trials.models import Trial


class SearchResultSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source="industry.name", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Trial
        fields = [
            "id",
            "title",
            "description",
            "industry_name",
            "company_name",
            "location",
            "is_featured",
            "created_at",
        ]
