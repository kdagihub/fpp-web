"""
Settings de production.
Hérite de base.py et renforce la sécurité.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CORS_ALLOWED_ORIGINS = [
    "https://fpp.monajent.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://fpp.monajent.com",
    "https://api-fpp.monajent.com",
]

SIMPLE_JWT["AUTH_COOKIE_SECURE"] = True  # noqa: F405

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]
