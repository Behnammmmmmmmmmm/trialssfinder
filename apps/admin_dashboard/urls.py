"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    # Dashboard
    path("dashboard/stats/", views.dashboard_stats, name="admin-dashboard-stats"),
    path("dashboard/growth/", views.growth_metrics, name="admin-growth-metrics"),
    path("dashboard/health/", views.system_health, name="admin-system-health"),
    # User Management
    path("users/", views.user_management, name="admin-user-management"),
    path("users/<int:user_id>/action/", views.user_action, name="admin-user-action"),
    # Trial Management
    path("trials/", views.trial_management, name="admin-trial-management"),
    path("trials/<int:trial_id>/action/", views.trial_action, name="admin-trial-action"),
    path("trials/bulk-action/", views.bulk_trial_action, name="admin-bulk-trial-action"),
    # Analytics
    path("analytics/revenue/", views.revenue_analytics, name="admin-revenue-analytics"),
    # System
    path("config/", views.system_config, name="admin-system-config"),
    path("activity-log/", views.admin_activity_log, name="admin-activity-log"),
    path("export/", views.export_data, name="admin-export-data"),
    path("report/", views.generate_report, name="admin-generate-report"),
    path("search/", views.search_everything, name="admin-search"),
]
