"""DRF serializers for API."""
from django.utils.html import escape
from rest_framework import serializers

from .models import FavoriteTrial, Industry, Trial, UserIndustry


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ["id", "name"]


class TrialSerializer(serializers.ModelSerializer):
    industry_name = serializers.CharField(source="industry.name", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Trial
        fields = [
            "id",
            "title",
            "description",
            "industry",
            "industry_name",
            "company_name",
            "location",
            "start_date",
            "end_date",
            "status",
            "is_featured",
            "created_at",
            "updated_at",
            "is_favorited",
        ]
        read_only_fields = ["status", "is_featured", "created_at", "updated_at"]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return FavoriteTrial.objects.filter(user=request.user, trial=obj).exists()
        return False

    def validate_title(self, value):
        """Sanitize title to prevent XSS."""
        return escape(value)

    def validate_description(self, value):
        """Sanitize description to prevent XSS."""
        return escape(value)

    def validate_location(self, value):
        """Sanitize location to prevent XSS."""
        return escape(value)


class FavoriteTrialSerializer(serializers.ModelSerializer):
    trial = TrialSerializer(read_only=True)

    class Meta:
        model = FavoriteTrial
        fields = ["id", "trial", "created_at"]


class UserIndustrySerializer(serializers.ModelSerializer):
    industry = IndustrySerializer(read_only=True)

    class Meta:
        model = UserIndustry
        fields = ["id", "industry"]
