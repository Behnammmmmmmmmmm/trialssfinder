# URL patterns
from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.client_logs, name='client_logs'),  # Added trailing slash
]