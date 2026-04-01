from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


class PartyRole(TimeStampedModel):
    """Rôle politique au sein du parti (créé dynamiquement)."""

    class LevelChoices(models.TextChoices):
        NATIONAL = "national", "National"
        REGIONAL = "regional", "Régional"
        COMMUNAL = "communal", "Communal"
        LOCAL = "local", "Local"

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    level = models.CharField(max_length=20, choices=LevelChoices.choices, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Rôle du parti"
        verbose_name_plural = "Rôles du parti"
        ordering = ["level", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class UserPartyRole(TimeStampedModel):
    """Table de liaison M2M — affectation d'un rôle à un membre, éventuellement dans une zone."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="party_roles",
        db_index=True,
    )
    role = models.ForeignKey(
        PartyRole,
        on_delete=models.CASCADE,
        related_name="holders",
        db_index=True,
    )
    zone = models.ForeignKey(
        "zones.Zone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roles_assigned",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Affectation de rôle"
        verbose_name_plural = "Affectations de rôles"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role", "zone"],
                condition=models.Q(is_active=True),
                name="unique_active_user_role_zone",
            )
        ]

    def __str__(self):
        zone_str = f" — {self.zone}" if self.zone else ""
        return f"{self.user} → {self.role}{zone_str}"
