"""API views and endpoints."""
import logging

from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)

logger = logging.getLogger("trialssfinder.auth")


class AuthThrottle(AnonRateThrottle):
    rate = "5/hour"

    def get_rate(self):
        """
        Return the rate limit for authentication endpoints
        ."""
        return self.rate

    def throttled(self, request, wait):
        """
        Override throttled method to customize the response when rate limit is exceeded
        ."""
        from rest_framework.exceptions import Throttled

        raise Throttled(wait)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.verification_token = get_random_string(64)
        user.save()

        # Create company profile if user_type is company
        if user.user_type == "company":
            from apps.companies.models import Company

            # Use provided company name or default
            company_name = request.data.get("company_name", f"{user.username}'s Company")
            Company.objects.create(
                user=user,
                name=company_name,
                address=request.data.get("address", ""),
                phone=request.data.get("phone", ""),
                website=request.data.get("website", ""),
            )

        refresh = RefreshToken.for_user(user)

        # Send verification email
        from apps.core.email_utils import EmailService

        try:
            EmailService.send_verification_email(user, user.verification_token)
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "verification_token": user.verification_token,  # For frontend to handle
                "message": "Registration successful. Please check your email to verify your account.",
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)

        # Determine redirect based on user type
        if user.user_type == "company":
            redirect_to = "/dashboard"
        elif user.user_type == "admin":
            redirect_to = "/admin"
        else:
            redirect_to = "/profile"

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "redirect_to": redirect_to,
            }
        )
    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email(request):
    token = request.data.get("token", "")
    if not token:
        return Response({"error": "Token required"}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, verification_token=token)
    user.email_verified = True
    user.verification_token = ""
    user.save()

    # Return user type for frontend redirect
    redirect_to = "/dashboard" if user.user_type == "company" else "/profile"

    return Response({"message": "Email verified successfully", "user_type": user.user_type, "redirect_to": redirect_to})


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AuthThrottle])
def forgot_password(request):
    email = request.data.get("email", "")

    try:
        user = User.objects.get(email=email)
        user.reset_token = get_random_string(64)
        user.save()

        # Send reset email
        from apps.core.email_utils import EmailService

        try:
            EmailService.send_password_reset_email(user, user.reset_token)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")

        return Response(
            {"message": "If your email is associated with an account, you'll receive a link to reset your password."}
        )
    except User.DoesNotExist:
        # Return same message to prevent email enumeration
        return Response(
            {"message": "If your email is associated with an account, you'll receive a link to reset your password."}
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        user = get_object_or_404(User, reset_token=token)
        user.set_password(password)
        user.reset_token = ""
        user.save()

        return Response({"message": "Password reset successfully"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def me(request):
    serializer = UserSerializer(request.user)
    data = serializer.data

    # Add company info if user is a company
    if request.user.user_type == "company" and hasattr(request.user, "company"):
        from apps.companies.serializers import CompanySerializer

        data["company"] = CompanySerializer(request.user.company).data

    return Response(data)
