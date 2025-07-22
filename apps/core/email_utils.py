"""Module implementation."""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("trialssfinder.email")


class EmailService:
    """Centralized email service."""

    @staticmethod
    def send_email(template_name, context, to_email, subject=None):
        """Send HTML email using template."""
        try:
            # Add common context
            context["site_url"] = settings.SITE_URL
            context["support_email"] = "support@trialsfinder.com"

            # Try to render HTML template
            try:
                html_content = render_to_string(f"core/email_templates/{template_name}.html", context)
                text_content = strip_tags(html_content)
            except Exception as template_error:
                logger.warning(f"Template {template_name}.html not found, using fallback: {str(template_error)}")
                # Fallback to simple text email
                text_content = f"""
                {subject or 'TrialsFinder Notification'}
                
                {context.get('message', 'You have a new notification from TrialsFinder.')}
                
                Visit {settings.SITE_URL} to learn more.
                
                Best regards,
                TrialsFinder Team
                """
                html_content = f"<html><body>{text_content.replace(chr(10), '<br>')}</body></html>"

            # Use subject from context if not provided
            if not subject:
                subject = context.get("subject", "TrialsFinder Notification")

            # Create email
            email = EmailMultiAlternatives(
                subject=subject, body=text_content, from_email=settings.DEFAULT_FROM_EMAIL, to=[to_email]
            )
            email.attach_alternative(html_content, "text/html")

            # Send
            email.send(fail_silently=True)  # Don't crash on email failures
            logger.info(f"Email sent: {template_name} to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Email failed: {template_name} to {to_email} - {str(e)}")
            return False

    @staticmethod
    def send_welcome_email(user):
        return EmailService.send_email("welcome", {"username": user.username}, user.email, "Welcome to TrialsFinder!")

    @staticmethod
    def send_verification_email(user, token):
        return EmailService.send_email(
            "verify_email",
            {"username": user.username, "verification_url": f"{settings.SITE_URL}/verify-email?token={token}"},
            user.email,
            "Verify Your Email",
        )

    @staticmethod
    def send_password_reset_email(user, token):
        return EmailService.send_email(
            "password_reset",
            {"username": user.username, "reset_url": f"{settings.SITE_URL}/reset-password?token={token}"},
            user.email,
            "Reset Your Password",
        )

    @staticmethod
    def send_trial_approved_email(trial):
        return EmailService.send_email(
            "trial_approved",
            {"trial_title": trial.title, "trial_url": f"{settings.SITE_URL}/trials/{trial.id}"},
            trial.company.user.email,
            "Trial Approved!",
        )

    @staticmethod
    def send_trial_rejected_email(trial, reason):
        return EmailService.send_email(
            "trial_rejected",
            {"trial_title": trial.title, "reason": reason, "edit_url": f"{settings.SITE_URL}/edit-trial/{trial.id}"},
            trial.company.user.email,
            "Trial Needs Revision",
        )

    @staticmethod
    def send_new_trial_notification(user, trial):
        return EmailService.send_email(
            "new_trial_notification",
            {
                "industry": trial.industry.name,
                "trial_title": trial.title,
                "trial_description": trial.description,
                "trial_url": f"{settings.SITE_URL}/trials/{trial.id}",
            },
            user.email,
            f"New Trial: {trial.title}",
        )

    @staticmethod
    def send_subscription_created_email(subscription):
        from datetime import timedelta

        return EmailService.send_email(
            "subscription_created",
            {
                "trial_title": subscription.trial.title,
                "amount": subscription.amount,
                "next_billing_date": (subscription.created_at + timedelta(days=30)).strftime("%B %d, %Y"),
                "subscription_url": f"{settings.SITE_URL}/subscription",
            },
            subscription.company.user.email,
            "Subscription Confirmed",
        )

    @staticmethod
    def send_payment_failed_email(subscription):
        return EmailService.send_email(
            "payment_failed",
            {"trial_title": subscription.trial.title, "payment_url": f"{settings.SITE_URL}/subscription"},
            subscription.company.user.email,
            "Payment Failed",
        )

    @staticmethod
    def send_trial_expiring_email(trial, days_left):
        return EmailService.send_email(
            "trial_expiring",
            {"trial_title": trial.title, "days_left": days_left, "trial_url": f"{settings.SITE_URL}/trials/{trial.id}"},
            trial.company.user.email,
            "Trial Expiring Soon",
        )

    @staticmethod
    def send_weekly_digest(user, new_trials):
        return EmailService.send_email(
            "weekly_digest",
            {
                "new_trials": [
                    {
                        "title": trial.title,
                        "industry": trial.industry.name,
                        "url": f"{settings.SITE_URL}/trials/{trial.id}",
                    }
                    for trial in new_trials
                ]
            },
            user.email,
            "Your Weekly TrialsFinder Update",
        )

    @staticmethod
    def send_deletion_verification_email(user, token):
        return EmailService.send_email(
            "deletion_verification",
            {"username": user.username, "deletion_url": f"{settings.SITE_URL}/confirm-deletion?token={token}"},
            user.email,
            "Confirm Account Deletion",
        )