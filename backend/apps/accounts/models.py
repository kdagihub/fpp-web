import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur custom — connexion par email."""

    class SexChoices(models.TextChoices):
        MALE = "M", "Masculin"
        FEMALE = "F", "Féminin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, unique=True, db_index=True, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=1, choices=SexChoices.choices, blank=True, default="")
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_emergency_user = models.BooleanField(
        default=False,
        help_text="Peut déclencher la procédure de purge d'urgence.",
    )

    cgu_accepted_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="CGU acceptées le",
    )
    privacy_accepted_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Politique de confidentialité acceptée le",
    )
    cgu_ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name="IP lors du consentement",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "is_staff"], name="idx_user_active_staff"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class ConsentLog(models.Model):
    """Historique immuable des consentements — Loi 2013-450 art. 33."""

    class ConsentType(models.TextChoices):
        CGU = "cgu", "Conditions Générales d'Utilisation"
        PRIVACY = "privacy", "Politique de Confidentialité"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consent_logs",
    )
    consent_type = models.CharField(max_length=10, choices=ConsentType.choices)
    version = models.CharField(max_length=20, default="1.0")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    accepted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Journal de consentement"
        verbose_name_plural = "Journaux de consentement"
        ordering = ["-accepted_at"]

    def __str__(self):
        return f"{self.user} — {self.get_consent_type_display()} v{self.version} ({self.accepted_at:%d/%m/%Y %H:%M})"
