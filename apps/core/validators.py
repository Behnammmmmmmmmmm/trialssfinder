"""Module implementation."""
import re

from django.core.exceptions import ValidationError

import bleach

from trialssfinder.security_config import SECURITY_CONFIG


class InputValidator:
    """Centralized input validation"""

    @staticmethod
    def validate_username(username):
        pattern = SECURITY_CONFIG["INPUT_VALIDATION"]["REGEX_PATTERNS"]["username"]
        if not re.match(pattern, username):
            raise ValidationError("Username must be 3-30 characters, alphanumeric with _ or -")
        return username

    @staticmethod
    def validate_email(email):
        pattern = SECURITY_CONFIG["INPUT_VALIDATION"]["REGEX_PATTERNS"]["email"]
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")
        return email.lower()

    @staticmethod
    def validate_phone(phone):
        pattern = SECURITY_CONFIG["INPUT_VALIDATION"]["REGEX_PATTERNS"]["phone"]
        if not re.match(pattern, phone):
            raise ValidationError("Invalid phone number format")
        return phone

    @staticmethod
    def sanitize_html(text):
        """Remove all HTML tags and entities."""
        if not text:
            return text
        # Use bleach to clean HTML
        cleaned = bleach.clean(text, tags=[], strip=True)
        return cleaned

    @staticmethod
    def validate_text_input(text, max_length=None):
        """Validate and sanitize text input."""
        if not text:
            return text

        # Check length
        max_len = max_length or SECURITY_CONFIG["INPUT_VALIDATION"]["MAX_INPUT_LENGTH"]
        if len(text) > max_len:
            raise ValidationError(f"Input too long. Maximum {max_len} characters allowed.")

        # Sanitize
        return InputValidator.sanitize_html(text)

    @staticmethod
    def validate_integer(value, min_val=None, max_val=None):
        """Validate integer input."""
        try:
            int_val = int(value)
            if min_val is not None and int_val < min_val:
                raise ValidationError(f"Value must be at least {min_val}")
            if max_val is not None and int_val > max_val:
                raise ValidationError(f"Value must be at most {max_val}")
            return int_val
        except (TypeError, ValueError):
            raise ValidationError("Invalid integer value")
