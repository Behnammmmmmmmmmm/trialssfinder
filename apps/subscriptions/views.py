"""API views and endpoints."""
import uuid

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.trials.models import Trial

from .models import Invoice, PaymentMethod, Subscription
from .serializers import InvoiceSerializer, PaymentMethodSerializer, SubscriptionSerializer


@api_view(["GET", "POST"])
def payment_methods(request):
    company = request.user.company

    if request.method == "GET":
        methods = PaymentMethod.objects.filter(company=company)
        serializer = PaymentMethodSerializer(methods, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        # Create payment method with proper fields
        data = request.data.copy()

        # Map old field names to new ones if needed
        if "method_type" in data:
            data["provider"] = data.pop("method_type", "stripe")
        if "last_four" in data:
            data["card_last4"] = data.pop("last_four")

        # Set defaults for required fields
        data.setdefault("provider", "stripe")
        data.setdefault("card_brand", "unknown")

        payment_method = PaymentMethod(
            company=company,
            provider=data.get("provider", "stripe"),
            card_last4=data.get("card_last4", ""),
            card_brand=data.get("card_brand", "unknown"),
            is_default=data.get("is_default", False),
        )

        if payment_method.is_default:
            PaymentMethod.objects.filter(company=company).update(is_default=False)

        payment_method.save()
        serializer = PaymentMethodSerializer(payment_method)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
def delete_payment_method(request, pk):
    # Handle both string UUID and UUID object
    if isinstance(pk, str):
        try:
            pk = uuid.UUID(pk)
        except ValueError:
            return Response({"error": "Invalid payment method ID"}, status=status.HTTP_400_BAD_REQUEST)

    method = get_object_or_404(PaymentMethod, pk=pk, company=request.user.company)
    method.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def set_default_payment_method(request, pk):
    # Handle both string UUID and UUID object
    if isinstance(pk, str):
        try:
            pk = uuid.UUID(pk)
        except ValueError:
            return Response({"error": "Invalid payment method ID"}, status=status.HTTP_400_BAD_REQUEST)

    method = get_object_or_404(PaymentMethod, pk=pk, company=request.user.company)
    PaymentMethod.objects.filter(company=method.company).update(is_default=False)
    method.is_default = True
    method.save()
    return Response({"message": "Default payment method updated"})


@api_view(["GET"])
def subscriptions(request):
    subs = Subscription.objects.filter(company=request.user.company).select_related("trial")
    serializer = SubscriptionSerializer(subs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def create_subscription(request):
    trial_id = request.data.get("trial_id")
    payment_method_id = request.data.get("payment_method_id")

    # Convert string UUID to UUID object if needed
    if isinstance(payment_method_id, str):
        try:
            payment_method_id = uuid.UUID(payment_method_id)
        except ValueError:
            return Response({"error": "Invalid payment method ID"}, status=status.HTTP_400_BAD_REQUEST)

    trial = get_object_or_404(Trial, pk=trial_id)
    payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id, company=request.user.company)

    # Check if subscription already exists
    if Subscription.objects.filter(company=request.user.company, trial=trial).exists():
        return Response({"error": "Subscription already exists for this trial"}, status=status.HTTP_400_BAD_REQUEST)

    subscription = Subscription.objects.create(
        company=request.user.company, trial=trial, payment_method=payment_method, amount=trial.price
    )

    Invoice.objects.create(subscription=subscription, amount=subscription.amount)

    trial.status = "under_review"
    trial.save()

    return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def invoices(request):
    company_invoices = Invoice.objects.filter(subscription__company=request.user.company).select_related(
        "subscription__trial"
    )
    serializer = InvoiceSerializer(company_invoices, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def update_address(request):
    company = request.user.company
    company.address = request.data.get("address", company.address)
    company.save()
    return Response({"message": "Address updated", "address": company.address})
