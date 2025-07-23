# URL patterns
from django.urls import path
from . import views

urlpatterns = [
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('payment-methods/<str:pk>/', views.delete_payment_method, name='delete_payment_method'),
    path('payment-methods/<str:pk>/set-default/', views.set_default_payment_method, name='set_default_payment_method'),
    path('', views.subscriptions, name='subscriptions_list'),
    path('create/', views.create_subscription, name='create_subscription'),
    path('invoices/', views.invoices, name='invoices_list'),
    path('update-address/', views.update_address, name='update_address'),
]