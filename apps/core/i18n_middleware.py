"""Module implementation."""

from django.conf import settings
from django.utils import translation


class LanguageMiddleware:
    """Enhanced language detection middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try to get language from:
        # 1. URL parameter
        # 2. Session
        # 3. Cookie
        # 4. Accept-Language header
        # 5. User preference (if authenticated)

        language = None

        # Check user preference
        if request.user.is_authenticated and hasattr(request.user, "language_preference"):
            language = request.user.language_preference

        # Check Accept-Language header
        if not language:
            accept_lang = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
            for lang_code, _ in settings.LANGUAGES:
                if lang_code in accept_lang:
                    language = lang_code
                    break

        if language and language in dict(settings.LANGUAGES):
            translation.activate(language)
        else:
            translation.activate(settings.LANGUAGE_CODE)

        request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)

        # Set Content-Language header
        response["Content-Language"] = translation.get_language()

        # Set text direction for RTL languages
        if translation.get_language() in ["ar", "he", "fa", "ur"]:
            response["X-Text-Direction"] = "rtl"
        else:
            response["X-Text-Direction"] = "ltr"

        return response
