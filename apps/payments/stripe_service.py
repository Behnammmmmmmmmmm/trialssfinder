"""Module implementation."""
import logging
from typing import Any, Dict, Optional

from django.conf import settings

import stripe

from apps.companies.models import Company

logger = logging.getLogger("trialssfinder.payments")


class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    def create_customer(self, company: "Company") -> Dict[str, Any]:
        """Create Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=company.user.email,
                name=company.name,
                metadata={"company_id": str(company.id), "user_id": str(company.user.id)},
            )
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {str(e)}")
            raise

    def create_setup_intent(self, customer_id: str) -> Dict[str, Any]:
        """Create setup intent for adding payment method."""
        try:
            setup_intent = stripe.SetupIntent.create(
                customer=customer_id, payment_method_types=["card"], usage="off_session"
            )
            return setup_intent
        except stripe.error.StripeError as e:
            logger.error(f"Setup intent creation failed: {str(e)}")
            raise

    def attach_payment_method(self, payment_method_id: str, customer_id: str) -> Dict[str, Any]:
        """Attach payment method to customer."""
        try:
            payment_method = stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

            # Set as default
            stripe.Customer.modify(customer_id, invoice_settings={"default_payment_method": payment_method_id})

            return payment_method
        except stripe.error.StripeError as e:
            logger.error(f"Payment method attachment failed: {str(e)}")
            raise

    def create_subscription(self, customer_id: str, price_id: str, trial_days: int = 0) -> Dict[str, Any]:
        """Create subscription."""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days,
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent", "pending_setup_intent"],
            )
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Subscription creation failed: {str(e)}")
            raise

    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        """Cancel subscription."""
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
            else:
                subscription = stripe.Subscription.retrieve(subscription_id)
            subscription.delete()
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Subscription cancellation failed: {str(e)}")
            raise

    def create_refund(self, payment_intent_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Create refund."""
        try:
            refund_data = {"payment_intent": payment_intent_id}
            if amount:
                refund_data["amount"] = amount

            refund = stripe.Refund.create(**refund_data)
            return refund
        except stripe.error.StripeError as e:
            logger.error(f"Refund creation failed: {str(e)}")
            raise

    def retrieve_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Retrieve invoice details."""
        try:
            invoice = stripe.Invoice.retrieve(invoice_id, expand=["subscription", "payment_intent"])
            return invoice
        except stripe.error.StripeError as e:
            logger.error(f"Invoice retrieval failed: {str(e)}")
            raise

    def verify_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Verify webhook signature."""
        try:
            event = stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise
