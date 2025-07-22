"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.company_profile, name="profile"),
]
