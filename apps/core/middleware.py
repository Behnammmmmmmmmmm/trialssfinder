"""Middleware for request processing and security."""
import hashlib
import json
import logging
import re
import time
import uuid

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.utils.cache import (
    add_never_cache_headers,
    get_cache_key,
    get_max_age,
    has_vary_header,
    learn_cache_key,
    patch_cache_control,
    patch_response_headers,
)
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("trialssfinder.requests")


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add comprehensive security headers to all responses."""

    def process_response(self, request, response):
        # Security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove sensitive headers
        response["Server"] = "TrialsFinder"
        if "X-Powered-By" in response:
            del response["X-Powered-By"]
        
        # HSTS header (only on HTTPS)
        if request.is_secure():
            response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response


class CacheControlMiddleware(MiddlewareMixin):
    """Enhanced cache control middleware."""
    
    def process_response(self, request, response):
        # Skip if already has cache headers
        if response.has_header('Cache-Control'):
            return response
        
        # Don't cache errors
        if response.status_code >= 400:
            add_never_cache_headers(response)
            return response
        
        # Don't cache authenticated responses
        if hasattr(request, 'user') and request.user.is_authenticated:
            patch_cache_control(response, private=True, max_age=0)
            return response
        
        path = request.path
        
        # Static files - aggressive caching
        if path.startswith('/static/'):
            if settings.DEBUG:
                patch_cache_control(response, public=True, max_age=300)  # 5 minutes in dev
            else:
                patch_cache_control(response, public=True, max_age=31536000, immutable=True)  # 1 year
            return response
        
        # API responses
        if path.startswith('/api/'):
            # Auth endpoints - no cache
            if '/auth/' in path:
                add_never_cache_headers(response)
            # GET requests - cache
            elif request.method == 'GET':
                # Different cache times for different endpoints
                if '/industries/' in path:
                    patch_cache_control(response, public=True, max_age=3600)  # 1 hour
                elif '/trials/' in path:
                    if re.match(r'/api/trials/\d+/$', path):  # Detail view
                        patch_cache_control(response, public=True, max_age=600)  # 10 minutes
                    else:  # List view
                        patch_cache_control(response, public=True, max_age=300)  # 5 minutes
                else:
                    patch_cache_control(response, public=True, max_age=60)  # 1 minute
            else:
                # Non-GET requests
                add_never_cache_headers(response)
            return response
        
        # HTML pages
        if response.get('Content-Type', '').startswith('text/html'):
            # Service worker
            if path == '/service-worker.js':
                add_never_cache_headers(response)
            # Index page - short cache
            elif path == '/':
                patch_cache_control(response, public=True, max_age=300)  # 5 minutes
            else:
                patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True)
        
        return response


class CompressionMiddleware(MiddlewareMixin):
    """Enhanced compression middleware."""
    
    def process_response(self, request, response):
        # Skip if already compressed
        if response.has_header('Content-Encoding'):
            return response
        
        # Check if client accepts gzip
        ae = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in ae:
            return response
        
        # Only compress certain content types
        ct = response.get('Content-Type', '').lower()
        compressible_types = (
            'text/', 'application/json', 'application/javascript',
            'application/xml', 'application/rss+xml', 'image/svg+xml'
        )
        
        if not any(ct.startswith(t) for t in compressible_types):
            return response
        
        # Don't compress small responses
        if len(response.content) < 200:
            return response
        
        # Compress
        import gzip
        compressed_content = gzip.compress(response.content)
        
        # Only use if smaller
        if len(compressed_content) < len(response.content):
            response.content = compressed_content
            response['Content-Encoding'] = 'gzip'
            response['Content-Length'] = str(len(compressed_content))
        
        return response


class ETAGMiddleware(MiddlewareMixin):
    """Add ETags for better caching."""
    
    def process_response(self, request, response):
        # Skip if already has ETag
        if response.has_header('ETag'):
            return response
        
        # Only for GET/HEAD requests
        if request.method not in ('GET', 'HEAD'):
            return response
        
        # Only for 200 responses
        if response.status_code != 200:
            return response
        
        # Generate ETag
        content = response.content
        etag = f'"{hashlib.md5(content).hexdigest()}"'
        response['ETag'] = etag
        
        # Check If-None-Match
        if_none_match = request.META.get('HTTP_IF_NONE_MATCH')
        if if_none_match == etag:
            response = HttpResponse(status=304)
            response['ETag'] = etag
        
        return response