from django.db import models

from apps.core.models import TimeStampedModel


class SiteSettings(TimeStampedModel):
    """Paramètres globaux du site — singleton (une seule ligne en base)."""

    site_name = models.CharField(max_length=200, default="FPP - Front Patriotique Panafricain")
    slogan = models.CharField(max_length=300, blank=True, default="")
    president_name = models.CharField(max_length=200, blank=True, default="")
    president_message = models.TextField(blank=True, default="")
    president_photo = models.ImageField(upload_to="settings/", blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, default="")
    contact_email = models.EmailField(blank=True, default="")
    address = models.TextField(blank=True, default="")

    facebook_url = models.URLField(blank=True, default="")
    twitter_url = models.URLField(blank=True, default="")
    instagram_url = models.URLField(blank=True, default="")
    youtube_url = models.URLField(blank=True, default="")

    logo = models.ImageField(upload_to="settings/", blank=True, null=True)
    hero_image = models.ImageField(upload_to="settings/", blank=True, null=True)
    hero_title = models.CharField(max_length=200, blank=True, default="")
    hero_subtitle = models.TextField(blank=True, default="")
    about_text = models.TextField(blank=True, default="")
    vision_text = models.TextField(blank=True, default="")
    values_text = models.TextField(blank=True, default="")

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = self.pk or SiteSettings.objects.first()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Charge ou crée l'instance singleton."""
        obj, _ = cls.objects.get_or_create(pk=cls.objects.first().pk if cls.objects.exists() else None)
        return obj


class BureauMember(TimeStampedModel):
    """Membre du Bureau National — affiché sur la page 'Le Parti'."""

    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=300, help_text="Fonction ou titre au sein du parti")
    photo = models.ImageField(upload_to="bureau/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Membre du bureau"
        verbose_name_plural = "Membres du bureau"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.title}"
