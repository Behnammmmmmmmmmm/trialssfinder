"""
Production settings for TrialsFinder
"""
import os
import logging

import dj_database_url
import sentry_sdk
from decouple import config
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .settings import *

# Override base settings for production
DEBUG = False

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Session security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_FAILURE_VIEW = "apps.core.views.csrf_failure"

# Database
DATABASES = {"default": dj_database_url.config(default=config("DATABASE_URL"), conn_max_age=600, ssl_require=True)}

# Add database connection pooling
DATABASES["default"]["OPTIONS"] = {
    "connect_timeout": 10,
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5,
}

# Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
            },
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "trialssfinder:prod",
        "TIMEOUT": 300,
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL") + "/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "session",
        "TIMEOUT": 86400,
    },
    "api": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL") + "/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "api",
        "TIMEOUT": 300,
    },
}

# Use Redis for sessions
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Static files (CSS, JavaScript, Images) - Using AWS S3
INSTALLED_APPS += ["storages"]

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_DEFAULT_ACL = "public-read"
AWS_S3_VERIFY = True

# Static files
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

# Media files
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@trialssfinder.com")

# Logging Configuration
from .logging_config import LOGGING

# GlitchTip Configuration - Enhanced for Production
GLITCHTIP_DSN = config("GLITCHTIP_DSN")

def before_send(event, hint):
    """Filter sensitive data before sending to GlitchTip"""
    # Filter out sensitive data
    if 'extra' in event:
        sensitive_keys = ['password', 'token', 'secret', 'api_key', 'stripe']
        for key in list(event['extra'].keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                event['extra'][key] = '[FILTERED]'
    
    # Filter request data
    if 'request' in event:
        if 'headers' in event['request']:
            for header in ['Authorization', 'Cookie', 'X-CSRFToken']:
                if header in event['request']['headers']:
                    event['request']['headers'][header] = '[FILTERED]'
        
        if 'data' in event['request']:
            for key in list(event['request']['data'].keys()):
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'card']):
                    event['request']['data'][key] = '[FILTERED]'
    
    return event

sentry_sdk.init(
    dsn=GLITCHTIP_DSN,
    integrations=[
        DjangoIntegration(
            transaction_style='function_name',
            middleware_spans=True,
            signals_spans=False,
        ),
        CeleryIntegration(
            monitor_beat_tasks=True,
            propagate_traces=True,
        ),
        RedisIntegration(),
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR,
        ),
    ],
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    send_default_pii=False,
    environment="production",
    release=f"trialssfinder@{config('VERSION', default='1.0.0')}",
    attach_stacktrace=True,
    request_bodies='medium',
    with_locals=False,
    max_breadcrumbs=50,
    debug=False,
    before_send=before_send,
    # Performance monitoring
    traces_sampler=lambda sampling_context: 0.1 if sampling_context.get('parent_sampled') is True else 0.01,
    # Additional options
    shutdown_timeout=5,
    in_app_include=['apps'],
    in_app_exclude=['django', 'celery', 'rest_framework'],
    default_integrations=False,
    auto_session_tracking=True,
    send_client_reports=True,
    # Error filtering
    ignore_errors=[
        'Http404',
        'KeyboardInterrupt',
        'SystemExit',
        'DisallowedHost',
        'PermissionDenied',
    ],
)

# Set custom GlitchTip tags
sentry_sdk.set_tag("server_name", config("SERVER_NAME", default="production"))
sentry_sdk.set_tag("deployment", config("DEPLOYMENT_ENV", default="production"))

# Additional Production Settings
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")])

# CORS in production - only allow specific origins
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")])
CORS_ALLOW_CREDENTIALS = True

# JWT Settings for production
from datetime import timedelta

SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=15)  # Shorter in production
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=7)
SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] = True
SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] = True
SIMPLE_JWT["UPDATE_LAST_LOGIN"] = True

# Celery Configuration for production
CELERY_BROKER_URL = config("REDIS_URL")
CELERY_RESULT_BACKEND = config("REDIS_URL")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10

# Rate limiting in production
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": "60/hour",
    "user": "600/hour",
}

# Stripe Production Keys
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")

# Elasticsearch Production Configuration
ELASTICSEARCH_URL = config("ELASTICSEARCH_URL")
ELASTICSEARCH_USER = config("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = config("ELASTICSEARCH_PASSWORD")
ELASTICSEARCH_INDEX = config("ELASTICSEARCH_INDEX", default="trialssfinder_prod")

# Site URL
SITE_URL = config("SITE_URL")

# Performance optimizations
CONN_MAX_AGE = 600  # Persistent database connections

# Security - Additional headers
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "camera": [],
    "geolocation": [],
    "microphone": [],
}

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = ("'self'", "https://api.stripe.com", "https://sentry.io")

# Update logging to include GlitchTip handler
LOGGING['handlers']['sentry'] = {
    'level': 'ERROR',
    'class': 'sentry_sdk.integrations.logging.EventHandler',
}

LOGGING['loggers']['django'] = {
    'handlers': ['console', 'sentry'],
    'level': 'INFO',
    'propagate': False,
}

LOGGING['loggers']['trialssfinder'] = {
    'handlers': ['console', 'sentry'],
    'level': 'INFO',
    'propagate': False,
}

LOGGING['loggers']['celery'] = {
    'handlers': ['console', 'sentry'],
    'level': 'INFO',
    'propagate': False,
}