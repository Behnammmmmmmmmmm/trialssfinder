from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    # Payment methods
    path('methods/', views.payment_methods, name='payment_methods'),
    path('methods/confirm/', views.confirm_payment_method, name='confirm_payment_method'),
    
    # Subscriptions
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('subscriptions/create/', views.create_subscription, name='create_subscription'),
    path('subscriptions/<str:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),
    
    # Invoices
    path('invoices/', views.invoices, name='invoices'),
    
    # Stripe webhook
    path('stripe/webhook/', csrf_exempt(views.stripe_webhook), name='stripe_webhook'),
]