"""URL patterns."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_notifications, name="user-notifications"),
    path("<int:pk>/read/", views.mark_notification_read, name="mark-notification-read"),
    path("contact/", views.contact_us, name="contact-us"),
]
