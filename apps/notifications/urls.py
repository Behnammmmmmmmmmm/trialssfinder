# URL patterns
from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_notifications, name='user_notifications'),
    path('<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('contact/', views.contact_us, name='contact_us'),
]