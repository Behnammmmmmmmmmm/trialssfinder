"""Celery background tasks."""
from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger

from apps.core.email_utils import EmailService

from .models import Invoice, PaymentEvent, Subscription

logger = get_task_logger(__name__)


@shared_task
def process_webhook_event(event_id):
    """Process payment webhook event"""
    try:
        event = PaymentEvent.objects.get(id=event_id)

        if event.processed:
            return

        if event.event_type == "invoice.payment_succeeded":
            handle_successful_payment(event)
        elif event.event_type == "invoice.payment_failed":
            handle_failed_payment(event)
        elif event.event_type == "customer.subscription.updated":
            handle_subscription_update(event)
        elif event.event_type == "customer.subscription.deleted":
            handle_subscription_deletion(event)

        event.processed = True
        event.save()

    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        event.error = str(e)
        event.save()
        raise


def handle_successful_payment(event):
    """Handle successful payment."""
    invoice_data = event.data["object"]

    try:
        subscription = Subscription.objects.get(provider_subscription_id=invoice_data["subscription"])

        # Create or update invoice
        invoice, created = Invoice.objects.update_or_create(
            provider_invoice_id=invoice_data["id"],
            defaults={
                "subscription": subscription,
                "invoice_number": invoice_data["number"],
                "status": "paid",
                "amount_paid": invoice_data["amount_paid"] / 100,
                "amount_due": invoice_data["amount_due"] / 100,
                "currency": invoice_data["currency"].upper(),
                "period_start": datetime.fromtimestamp(invoice_data["period_start"]),
                "period_end": datetime.fromtimestamp(invoice_data["period_end"]),
                "invoice_pdf": invoice_data.get("invoice_pdf", ""),
            },
        )

        # Send confirmation email
        EmailService.send_payment_successful_email(subscription)

    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found for invoice {invoice_data['id']}")


def handle_failed_payment(event):
    """Handle failed payment."""
    invoice_data = event.data["object"]

    try:
        subscription = Subscription.objects.get(provider_subscription_id=invoice_data["subscription"])

        # Update subscription status
        subscription.status = "past_due"
        subscription.save()

        # Send notification email
        EmailService.send_payment_failed_email(subscription)

    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found for invoice {invoice_data['id']}")


def handle_subscription_update(event):
    """Handle subscription update."""
    sub_data = event.data["object"]

    try:
        subscription = Subscription.objects.get(provider_subscription_id=sub_data["id"])

        subscription.status = sub_data["status"]
        subscription.current_period_start = datetime.fromtimestamp(sub_data["current_period_start"])
        subscription.current_period_end = datetime.fromtimestamp(sub_data["current_period_end"])
        subscription.cancel_at_period_end = sub_data["cancel_at_period_end"]
        subscription.save()

    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found: {sub_data['id']}")


def handle_subscription_deletion(event):
    """Handle subscription deletion."""
    sub_data = event.data["object"]

    try:
        subscription = Subscription.objects.get(provider_subscription_id=sub_data["id"])

        subscription.status = "canceled"
        subscription.save()

        # Send cancellation email
        EmailService.send_subscription_canceled_email(subscription)

    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found: {sub_data['id']}")


@shared_task
def check_expiring_subscriptions():
    """Check for subscriptions expiring soon."""
    from datetime import timedelta

    from django.utils import timezone

    # Check subscriptions expiring in 3 days
    expiry_date = timezone.now() + timedelta(days=3)

    expiring_subs = Subscription.objects.filter(
        status="active", current_period_end__date=expiry_date.date(), cancel_at_period_end=False
    )

    for subscription in expiring_subs:
        EmailService.send_subscription_expiring_email(subscription)
