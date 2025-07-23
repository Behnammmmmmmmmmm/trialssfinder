"""Module implementation."""
import logging
import traceback
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("trialssfinder.errors")


class TrialsFinderException(Exception):
    """Base exception for all custom exceptions."""

    default_message = "An error occurred"
    default_code = "error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self, message: Optional[str] = None, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None
    ):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(TrialsFinderException):
    default_message = "Validation failed"
    default_code = "validation_error"
    status_code = status.HTTP_400_BAD_REQUEST


class AuthenticationException(TrialsFinderException):
    default_message = "Authentication failed"
    default_code = "authentication_error"
    status_code = status.HTTP_401_UNAUTHORIZED


class PermissionException(TrialsFinderException):
    default_message = "Permission denied"
    default_code = "permission_error"
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundException(TrialsFinderException):
    default_message = "Resource not found"
    default_code = "not_found"
    status_code = status.HTTP_404_NOT_FOUND


class ConflictException(TrialsFinderException):
    default_message = "Resource conflict"
    default_code = "conflict"
    status_code = status.HTTP_409_CONFLICT


class ExternalServiceException(TrialsFinderException):
    default_message = "External service error"
    default_code = "external_service_error"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


def custom_exception_handler(exc, context):
    """Custom exception handler for DRF."""
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            "error": {
                "code": "http_error",
                "message": str(exc),
                "details": response.data if hasattr(response, "data") else {},
            }
        }
        response.data = custom_response_data
        return response

    # Handle custom exceptions
    if isinstance(exc, TrialsFinderException):
        logger.error(f"{exc.__class__.__name__}: {exc.message}", extra={"code": exc.code, "details": exc.details})
        
        return Response(
            {"error": {"code": exc.code, "message": exc.message, "details": exc.details}}, status=exc.status_code
        )

    # Handle Django validation errors
    elif isinstance(exc, DjangoValidationError):
        logger.warning(f"Validation error: {str(exc)}")
        return Response(
            {
                "error": {
                    "code": "validation_error",
                    "message": "Validation failed",
                    "details": {"errors": exc.message_dict if hasattr(exc, "message_dict") else str(exc)},
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle database integrity errors
    elif isinstance(exc, IntegrityError):
        logger.error(f"Database integrity error: {str(exc)}")
        
        return Response(
            {"error": {"code": "database_error", "message": "Database constraint violation", "details": {}}},
            status=status.HTTP_409_CONFLICT,
        )

    # Handle all other exceptions
    else:
        logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
        
        return Response(
            {"error": {"code": "internal_error", "message": "An unexpected error occurred", "details": {}}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )