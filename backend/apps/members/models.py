from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class MemberProfile(TimeStampedModel):
    """Profil membre — créé à la demande d'adhésion (Phase 2), pas à l'inscription."""

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "En attente"
        VALIDATED = "validated", "Validé"
        SUSPENDED = "suspended", "Suspendu"
        REJECTED = "rejected", "Rejeté"

    class IdDocumentType(models.TextChoices):
        CNI = "cni", "Carte Nationale d'Identité"
        PASSPORT = "passport", "Passeport"
        DRIVER_LICENSE = "driver_license", "Permis de conduire"

    class SourceChoices(models.TextChoices):
        WEB = "web", "Site web"
        MOBILE = "mobile", "Application mobile"
        ADMIN = "admin", "Saisie admin"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )
    matricule = models.CharField(max_length=30, unique=True, blank=True, null=True, db_index=True)
    id_document_type = models.CharField(
        max_length=20,
        choices=IdDocumentType.choices,
        default=IdDocumentType.CNI,
    )
    id_document_number = models.CharField(max_length=30, unique=True, db_index=True)
    id_document_scan = models.ImageField(upload_to="members/id_documents/")
    photo = models.ImageField(upload_to="members/photos/")
    profession = models.CharField(max_length=100, blank=True, default="")
    address = models.TextField(blank=True, default="")
    region = models.CharField(max_length=100, blank=True, default="", db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    commune = models.CharField(max_length=100, db_index=True)
    neighborhood = models.CharField(max_length=100, blank=True, default="")
    motivation = models.TextField(blank=True, default="")
    membership_status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
    )
    membership_date = models.DateTimeField(null=True, blank=True)
    registration_source = models.CharField(
        max_length=20,
        choices=SourceChoices.choices,
        default=SourceChoices.WEB,
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Profil membre"
        verbose_name_plural = "Profils membres"

    def __str__(self):
        label = self.matricule or "en attente"
        return f"{label} — {self.user.full_name}"
