"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.search_trials),
    path("suggest/", views.search_suggestions),
    path("track-click/", views.track_search_click),
    path("analytics/", views.search_analytics_dashboard),
]
