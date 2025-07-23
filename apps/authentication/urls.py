# URL patterns
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),  # Added trailing slash
    path('login/', views.login, name='login'),  # Added trailing slash
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Added trailing slash
    path('verify-email/', views.verify_email, name='verify_email'),  # Added trailing slash
    path('forgot-password/', views.forgot_password, name='forgot_password'),  # Added trailing slash
    path('reset-password/', views.reset_password, name='reset_password'),  # Added trailing slash
    path('me/', views.me, name='user_profile'),  # Added trailing slash
]