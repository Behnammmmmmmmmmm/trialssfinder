"""URL patterns."""
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify-email/", views.verify_email, name="verify-email"),
    path("forgot-password/", views.forgot_password, name="forgot-password"),
    path("reset-password/", views.reset_password, name="reset-password"),
    path("me/", views.me, name="user-profile"),
]
