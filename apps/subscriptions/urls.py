"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("payment-methods/", views.payment_methods, name="payment-methods"),
    path("payment-methods/<str:pk>/", views.delete_payment_method, name="delete-payment-method"),
    path("payment-methods/<str:pk>/set-default/", views.set_default_payment_method, name="set-default-payment-method"),
    path("", views.subscriptions, name="subscriptions-list"),
    path("create/", views.create_subscription, name="create-subscription"),
    path("invoices/", views.invoices, name="invoices-list"),
    path("update-address/", views.update_address, name="update-address"),
]
