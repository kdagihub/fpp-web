from django.conf import settings
from django.contrib import admin
from django.core.cache import cache
from django.template.response import TemplateResponse
from django.urls import path

from apps.emergency.tasks import CACHE_KEY_PREFIX


class EmergencyAdminSite:
    """Ajoute une vue custom dans l'admin Django pour surveiller
    l'état des codes d'urgence (sans modèle DB)."""

    @staticmethod
    def get_urls():
        return [
            path(
                "emergency/status/",
                admin.site.admin_view(EmergencyAdminSite.status_view),
                name="emergency-status",
            ),
        ]

    @staticmethod
    def status_view(request):
        emails = getattr(settings, "EMERGENCY_EMAILS", [])
        codes_status = []
        for email in emails:
            key = f"{CACHE_KEY_PREFIX}{email}"
            has_code = cache.get(key) is not None
            ttl = cache.ttl(key) if hasattr(cache, "ttl") else None
            codes_status.append({
                "email": email,
                "has_active_code": has_code,
                "ttl_seconds": ttl,
            })

        context = {
            **admin.site.each_context(request),
            "title": "État des codes d'urgence",
            "emails": codes_status,
            "total_emails": len(emails),
            "active_codes": sum(1 for c in codes_status if c["has_active_code"]),
        }
        return TemplateResponse(request, "admin/emergency_status.html", context)


original_get_urls = admin.AdminSite.get_urls


def patched_get_urls(self):
    custom = EmergencyAdminSite.get_urls()
    return custom + original_get_urls(self)


admin.AdminSite.get_urls = patched_get_urls
