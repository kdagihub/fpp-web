"""
Settings de production (Dokploy).
Hérite de base.py et renforce la sécurité.

Frontend : https://fpp-ci.online
Backend  : https://api.fpp-ci.online
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

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default=["api.fpp-ci.online", "fpp-backend"])  # noqa: F405

CORS_ALLOWED_ORIGINS = env(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    default=["https://fpp-ci.online", "https://www.fpp-ci.online"],
)

CSRF_TRUSTED_ORIGINS = [
    "https://fpp-ci.online",
    "https://www.fpp-ci.online",
    "https://api.fpp-ci.online",
]

SIMPLE_JWT["AUTH_COOKIE_SECURE"] = True  # noqa: F405
SIMPLE_JWT["AUTH_COOKIE_SAMESITE"] = "Lax"  # noqa: F405

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]

FRONTEND_URL = env("FRONTEND_URL", default="https://fpp-ci.online")  # noqa: F405
BACKEND_URL = env("BACKEND_URL", default="https://api.fpp-ci.online")  # noqa: F405
