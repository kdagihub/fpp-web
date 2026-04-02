from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import CanManageSettings
from apps.api.serializers.site_settings import (
    AdminSiteSettingsSerializer,
    PublicSiteSettingsSerializer,
)
from apps.core.mixins import AuditMixin
from apps.core.models import AuditLog
from apps.site_settings.models import SiteSettings


class PublicSiteSettingsView(APIView):
    """Parametres publics du site (nom, slogan, reseaux sociaux, hero, etc.)."""

    permission_classes = [AllowAny]

    def get(self, request):
        settings_obj = SiteSettings.load()
        serializer = PublicSiteSettingsSerializer(settings_obj)
        return Response(serializer.data)


class AdminSiteSettingsView(APIView):
    """Admin : consulter et modifier les parametres du site."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), CanManageSettings()]

    def get(self, request):
        settings_obj = SiteSettings.load()
        serializer = AdminSiteSettingsSerializer(settings_obj)
        return Response(serializer.data)

    def patch(self, request):
        settings_obj = SiteSettings.load()

        old_values = {
            field: str(getattr(settings_obj, field, ""))
            for field in request.data.keys()
            if hasattr(settings_obj, field) and field not in ("president_photo", "logo", "hero_image")
        }

        serializer = AdminSiteSettingsSerializer(
            settings_obj, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="SiteSettings",
            entity_id=settings_obj.pk,
            changes={k: {"old": v, "new": str(getattr(settings_obj, k, ""))} for k, v in old_values.items()},
            request=request,
        )

        return Response(serializer.data)
