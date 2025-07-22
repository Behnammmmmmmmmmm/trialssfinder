from django.utils import timezone

"""API views and endpoints."""
import json

from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import ConsentType, DataDeletionRequest, PolicyVersion, UserConsent, UserPolicyAcceptance
from .serializers import ConsentTypeSerializer, ConsentUpdateSerializer, PolicyVersionSerializer, UserConsentSerializer
from .tasks import export_user_data, process_deletion_request


@api_view(["GET"])
@permission_classes([AllowAny])
def get_consent_types(request):
    """Get all consent types."""
    consent_types = ConsentType.objects.all()
    serializer = ConsentTypeSerializer(consent_types, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_consents(request):
    """Get or update user consents."""
    if request.method == "GET":
        consents = UserConsent.objects.filter(user=request.user).select_related("consent_type").order_by("-created_at")

        # Get latest consent for each type
        latest_consents = {}
        for consent in consents:
            if consent.consent_type_id not in latest_consents:
                latest_consents[consent.consent_type_id] = consent

        serializer = UserConsentSerializer(latest_consents.values(), many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ConsentUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        with transaction.atomic():
            for consent_type_id, given in serializer.validated_data["consents"].items():
                consent_type = ConsentType.objects.get(id=consent_type_id)

                UserConsent.objects.create(
                    user=request.user,
                    consent_type=consent_type,
                    given=given,
                    version=settings.CONSENT_VERSION,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )

        return Response({"message": "Consents updated successfully"})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_policy(request, policy_type):
    """Get latest policy version."""
    try:
        policy = (
            PolicyVersion.objects.filter(policy_type=policy_type, effective_date__lte=timezone.now())
            .order_by("-effective_date")
            .first()
        )

        if not policy:
            return Response({"error": "Policy not found"}, status=404)

        serializer = PolicyVersionSerializer(policy)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_policy(request, policy_id):
    """Accept a policy version."""
    try:
        policy = PolicyVersion.objects.get(id=policy_id)

        acceptance, created = UserPolicyAcceptance.objects.get_or_create(
            user=request.user, policy_version=policy, defaults={"ip_address": request.META.get("REMOTE_ADDR")}
        )

        return Response(
            {"message": "Policy accepted" if created else "Already accepted", "accepted_at": acceptance.accepted_at}
        )
    except PolicyVersion.DoesNotExist:
        return Response({"error": "Policy not found"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_data_deletion(request):
    """Request account deletion (RTBF)."""
    from django.utils.crypto import get_random_string

    # Check if there's a pending request
    pending = DataDeletionRequest.objects.filter(user=request.user, status="pending").exists()

    if pending:
        return Response({"error": "You already have a pending deletion request"}, status=400)

    deletion_request = DataDeletionRequest.objects.create(
        user=request.user,
        request_type="deletion",
        reason=request.data.get("reason", ""),
        verification_token=get_random_string(64),
    )

    # Send verification email
    from apps.core.email_utils import EmailService

    EmailService.send_deletion_verification_email(request.user, deletion_request.verification_token)

    return Response(
        {"message": "Deletion request created. Please check your email to confirm.", "request_id": deletion_request.id}
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_deletion(request):
    """Confirm deletion request with token."""
    token = request.data.get("token")

    try:
        deletion_request = DataDeletionRequest.objects.get(verification_token=token, status="pending")

        deletion_request.status = "processing"
        deletion_request.save()

        # Process deletion asynchronously
        process_deletion_request.delay(deletion_request.id)

        return Response({"message": "Deletion request confirmed and is being processed"})
    except DataDeletionRequest.DoesNotExist:
        return Response({"error": "Invalid or expired token"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_data_export(request):
    """Request data export (portability)."""
    from django.utils.crypto import get_random_string

    export_request = DataDeletionRequest.objects.create(
        user=request.user, request_type="portability", verification_token=get_random_string(64)
    )

    # Process export asynchronously
    export_user_data.delay(export_request.id)

    return Response(
        {
            "message": "Data export request created. You will receive an email when ready.",
            "request_id": export_request.id,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def cookie_preferences(request):
    """Get/set cookie preferences without auth."""
    if request.method == "GET":
        # Get from cookie
        preferences = request.COOKIES.get("cookie_consent", "{}")
        try:
            preferences = json.loads(preferences)
        except Exception:
            preferences = {}

        return Response(preferences)
