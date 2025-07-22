"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("logs/", views.client_logs, name="client_logs"),
    path("test-sentry/", views.test_sentry, name="test_sentry"),  # REMOVE IN PRODUCTION
]