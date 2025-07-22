"""DRF serializers for API."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.companies.models import Company
from apps.trials.models import Trial

from .models import AdminAction, SystemConfig

User = get_user_model()


class AdminActionSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source="admin.username", read_only=True)

    class Meta:
        model = AdminAction
        fields = ["id", "admin", "admin_username", "action_type", "target_model", "target_id", "details", "timestamp"]


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ["key", "value", "description", "updated_by", "updated_at"]


class UserAdminSerializer(serializers.ModelSerializer):
    trials_count = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "user_type",
            "tier",
            "is_active",
            "email_verified",
            "date_joined",
            "last_login",
            "trials_count",
        ]

    def get_trials_count(self, obj):
        if hasattr(obj, "company"):
            return obj.company.trials.count()
        return 0


class CompanyAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    trials_count = serializers.IntegerField(source="trials.count", read_only=True)

    class Meta:
        model = Company
        fields = ["id", "name", "username", "email", "phone", "website", "created_at", "trials_count"]


class TrialAdminSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    industry_name = serializers.CharField(source="industry.name", read_only=True)
    views = serializers.SerializerMethodField()
    clicks = serializers.SerializerMethodField()

    class Meta:
        model = Trial
        fields = [
            "id",
            "title",
            "company_name",
            "industry_name",
            "location",
            "start_date",
            "end_date",
            "status",
            "is_featured",
            "created_at",
            "views",
            "clicks",
        ]

    def get_views(self, obj):
        return obj.analytics_events.filter(event_type="trial_view").count()

    def get_clicks(self, obj):
        return obj.analytics_events.filter(event_type="trial_start").count()


class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_companies = serializers.IntegerField()
    total_trials = serializers.IntegerField()
    pending_trials = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)


class SystemHealthSerializer(serializers.Serializer):
    database = serializers.DictField()
    cache = serializers.DictField()
    celery = serializers.DictField()
    storage = serializers.DictField()
