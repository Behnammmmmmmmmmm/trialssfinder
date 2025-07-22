"""API views and endpoints."""
import logging
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.trials.models import Trial

from .models import Invoice, PaymentEvent, PaymentMethod, Subscription
from .serializers import InvoiceSerializer, PaymentMethodSerializer, SubscriptionSerializer
from .stripe_service import StripeService
from .tasks import process_webhook_event

logger = logging.getLogger("trialssfinder.payments")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def payment_methods(request):
    """Manage payment methods."""
    company = request.user.company

    if request.method == "GET":
        methods = PaymentMethod.objects.filter(company=company)
        serializer = PaymentMethodSerializer(methods, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        stripe_service = StripeService()

        # Create setup intent
        try:
            # Get or create Stripe customer
            if not hasattr(company, "stripe_customer_id") or not company.stripe_customer_id:
                customer = stripe_service.create_customer(company)
                company.stripe_customer_id = customer["id"]
                company.save()

            setup_intent = stripe_service.create_setup_intent(company.stripe_customer_id)

            return Response({"client_secret": setup_intent["client_secret"], "public_key": settings.STRIPE_PUBLIC_KEY})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_payment_method(request):
    """Confirm payment method after client-side confirmation."""
    company = request.user.company
    payment_method_id = request.data.get("payment_method_id")

    if not payment_method_id:
        return Response({"error": "Payment method ID required"}, status=status.HTTP_400_BAD_REQUEST)

    stripe_service = StripeService()

    try:
        # Attach payment method
        payment_method = stripe_service.attach_payment_method(payment_method_id, company.stripe_customer_id)

        # Save to database
        db_payment_method = PaymentMethod.objects.create(
            company=company,
            provider="stripe",
            provider_customer_id=company.stripe_customer_id,
            provider_payment_method_id=payment_method["id"],
            card_last4=payment_method["card"]["last4"],
            card_brand=payment_method["card"]["brand"],
            is_default=True,
        )

        # Set other methods as non-default
        PaymentMethod.objects.filter(company=company).exclude(id=db_payment_method.id).update(is_default=False)

        serializer = PaymentMethodSerializer(db_payment_method)
        return Response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    """Create a new subscription."""
    company = request.user.company
    trial_id = request.data.get("trial_id")
    payment_method_id = request.data.get("payment_method_id")

    try:
        trial = Trial.objects.get(id=trial_id)
        payment_method = PaymentMethod.objects.get(id=payment_method_id, company=company)

        stripe_service = StripeService()

        # Create subscription in Stripe
        stripe_subscription = stripe_service.create_subscription(
            payment_method.provider_customer_id,
            trial.stripe_price_id,  # Assuming trial has stripe_price_id
            trial_days=7,  # 7-day trial
        )

        # Save to database
        subscription = Subscription.objects.create(
            company=company,
            trial=trial,
            payment_method=payment_method,
            provider_subscription_id=stripe_subscription["id"],
            status=stripe_subscription["status"],
            amount=trial.price,
            currency="USD",
            current_period_start=datetime.fromtimestamp(stripe_subscription["current_period_start"]),
            current_period_end=datetime.fromtimestamp(stripe_subscription["current_period_end"]),
        )

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Subscription creation failed: {str(e)}")
        return Response({"error": "Failed to create subscription"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subscriptions(request):
    """List user's subscriptions."""
    company = request.user.company
    subs = Subscription.objects.filter(company=company).select_related("trial")
    serializer = SubscriptionSerializer(subs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_subscription(request, subscription_id):
    """Cancel subscription."""
    try:
        subscription = Subscription.objects.get(id=subscription_id, company=request.user.company)

        stripe_service = StripeService()
        stripe_service.cancel_subscription(subscription.provider_subscription_id)

        subscription.cancel_at_period_end = True
        subscription.save()

        return Response({"message": "Subscription will be canceled at period end"})

    except Subscription.DoesNotExist:
        return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invoices(request):
    """List user's invoices."""
    company = request.user.company
    invoices = Invoice.objects.filter(subscription__company=company).select_related("subscription__trial")
    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks."""
    if request.method != "POST":
        return HttpResponse(status=405)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    stripe_service = StripeService()

    try:
        event = stripe_service.verify_webhook(payload, sig_header)

        # Save event
        payment_event = PaymentEvent.objects.create(
            provider="stripe", event_type=event["type"], provider_event_id=event["id"], data=event["data"]
        )

        # Process asynchronously
        process_webhook_event.delay(payment_event.id)

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        return HttpResponse(status=400)
