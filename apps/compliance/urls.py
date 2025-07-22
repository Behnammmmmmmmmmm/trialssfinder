"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("consent-types/", views.get_consent_types, name="consent-types"),
    path("consents/", views.user_consents, name="consents"),
    path("policy/<str:policy_type>/", views.get_policy, name="get-policy"),
    path("policy/<uuid:policy_id>/accept/", views.accept_policy, name="accept-policy"),
    path("deletion-request/", views.request_data_deletion, name="request-data-deletion"),
    path("deletion-confirm/", views.confirm_deletion, name="confirm-deletion"),
    path("data-export/", views.request_data_export, name="request-data-export"),
    path("cookie-preferences/", views.cookie_preferences, name="cookie-preferences"),
]
