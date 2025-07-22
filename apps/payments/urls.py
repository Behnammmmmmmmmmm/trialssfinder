"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("payment-methods/", views.payment_methods),
    path("payment-methods/confirm/", views.confirm_payment_method),
    path("subscriptions/", views.subscriptions),
    path("subscriptions/create/", views.create_subscription),
    path("subscriptions/<uuid:subscription_id>/cancel/", views.cancel_subscription),
    path("invoices/", views.invoices),
    path("webhook/stripe/", views.stripe_webhook),
]
