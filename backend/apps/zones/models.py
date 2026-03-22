from django.db import models

from apps.core.models import TimeStampedModel


class Zone(TimeStampedModel):
    """Zone géographique avec hiérarchie (Région → District → Commune → Quartier)."""

    class TypeChoices(models.TextChoices):
        REGION = "region", "Région"
        DISTRICT = "district", "District"
        COMMUNE = "commune", "Commune"
        QUARTIER = "quartier", "Quartier"

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TypeChoices.choices, db_index=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ["type", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
