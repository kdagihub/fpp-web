from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class UserSession(TimeStampedModel):
    """Suivi des sessions actives des utilisateurs authentifiés."""

    class DeviceTypeChoices(models.TextChoices):
        DESKTOP = "desktop", "Ordinateur"
        MOBILE = "mobile", "Mobile"
        TABLET = "tablet", "Tablette"
        UNKNOWN = "unknown", "Inconnu"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
        db_index=True,
    )
    session_key = models.CharField(max_length=64, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="")
    device = models.CharField(max_length=200, blank=True, default="")
    device_type = models.CharField(
        max_length=20,
        choices=DeviceTypeChoices.choices,
        default=DeviceTypeChoices.UNKNOWN,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    last_activity = models.DateTimeField(auto_now=True, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Session utilisateur"
        verbose_name_plural = "Sessions utilisateurs"

    def __str__(self):
        status = "active" if self.is_active else "terminée"
        return f"{self.user} — {self.device_type} ({status})"
