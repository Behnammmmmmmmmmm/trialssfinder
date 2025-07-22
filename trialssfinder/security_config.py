import os

# Security settings
SECURITY_CONFIG = {
    # API Security
    "API_KEY_HEADER": "X-API-Key",
    "API_RATE_LIMIT": {
        "DEFAULT": "100/hour",
        "AUTH": "1000/hour",
        "SENSITIVE": "10/hour",
    },
    # CORS Whitelist
    "CORS_WHITELIST": [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://api.yourdomain.com",
    ],
    # Security Headers
    "SECURITY_HEADERS": {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:;"
        ),
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    },
    # Input Validation Rules
    "INPUT_VALIDATION": {
        "MAX_INPUT_LENGTH": 10000,
        "ALLOWED_HTML_TAGS": [],
        "REGEX_PATTERNS": {
            "username": r"^[a-zA-Z0-9_-]{3,30}$",
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "phone": r"^[\d\s\-\+\(\)]+$",
        },
    },
}
