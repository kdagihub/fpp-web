import datetime

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class MemberProfile(TimeStampedModel):
    """Profil militant — lié 1:1 au User, créé à l'inscription."""

    class SexChoices(models.TextChoices):
        MALE = "M", "Masculin"
        FEMALE = "F", "Féminin"

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "En attente"
        VALIDATED = "validated", "Validé"
        SUSPENDED = "suspended", "Suspendu"
        REJECTED = "rejected", "Rejeté"

    class SourceChoices(models.TextChoices):
        WEB = "web", "Site web"
        MOBILE = "mobile", "Application mobile"
        ADMIN = "admin", "Saisie admin"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )
    matricule = models.CharField(max_length=20, unique=True, blank=True, db_index=True)
    sex = models.CharField(max_length=1, choices=SexChoices.choices)
    date_of_birth = models.DateField(null=True, blank=True)
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
    photo = models.ImageField(upload_to="members/photos/", blank=True, null=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Profil membre"
        verbose_name_plural = "Profils membres"

    def __str__(self):
        return f"{self.matricule} — {self.user.full_name}"

    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = self._generate_matricule()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_matricule():
        year = datetime.date.today().year
        last = (
            MemberProfile.objects.filter(matricule__startswith=f"FPP-{year}-")
            .order_by("-matricule")
            .values_list("matricule", flat=True)
            .first()
        )
        if last:
            seq = int(last.split("-")[-1]) + 1
        else:
            seq = 1
        return f"FPP-{year}-{seq:05d}"
