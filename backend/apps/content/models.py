from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """Catégorie d'articles."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(TimeStampedModel):
    """Article d'actualité ou de blog."""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        PUBLISHED = "published", "Publié"
        ARCHIVED = "archived", "Archivé"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.TextField(max_length=500)
    content = models.TextField()
    cover_image = models.ImageField(upload_to="articles/covers/", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        db_index=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    is_featured = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        indexes = [
            models.Index(fields=["status", "-published_at"], name="idx_article_status_pub"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class MediaContent(TimeStampedModel):
    """Contenu média (vidéo Facebook, YouTube, publication Facebook, etc.)."""

    class PlatformChoices(models.TextChoices):
        FACEBOOK = "facebook", "Facebook"
        YOUTUBE = "youtube", "YouTube"

    class EmbedTypeChoices(models.TextChoices):
        VIDEO = "video", "Vidéo"
        POST = "post", "Publication"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    platform = models.CharField(max_length=20, choices=PlatformChoices.choices)
    embed_type = models.CharField(
        max_length=20,
        choices=EmbedTypeChoices.choices,
        default=EmbedTypeChoices.VIDEO,
        help_text="'video' pour les vidéos/reels, 'post' pour les publications Facebook.",
    )
    source_url = models.URLField(
        max_length=500,
        help_text="URL Facebook complète ou ID vidéo YouTube.",
    )
    category = models.CharField(max_length=100, blank=True, default="")
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    published_at = models.DateField()

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Contenu média"
        verbose_name_plural = "Contenus médias"
        ordering = ["-published_at"]

    def __str__(self):
        return f"[{self.platform}] {self.title}"


# ===========================================================================
# Programme
# ===========================================================================

class ProgramSection(TimeStampedModel):
    """Section thématique du programme politique (ex: Éducation, Santé, Économie)."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(
        blank=True, default="",
        help_text="Introduction ou résumé de la section.",
    )
    icon = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Nom d'icône Lucide (ex: graduation-cap, heart-pulse, landmark).",
    )
    cover_image = models.ImageField(upload_to="programme/sections/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage.")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Section du programme"
        verbose_name_plural = "Sections du programme"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    @property
    def active_items(self):
        return self.items.filter(is_active=True).order_by("order", "title")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProgramItem(TimeStampedModel):
    """Mesure ou proposition concrète dans une section du programme."""

    section = models.ForeignKey(
        ProgramSection,
        on_delete=models.CASCADE,
        related_name="items",
    )
    title = models.CharField(max_length=300)
    description = models.TextField(help_text="Détail de la mesure.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Mesure du programme"
        verbose_name_plural = "Mesures du programme"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


# ===========================================================================
# Agenda / Événements
# ===========================================================================

class Event(TimeStampedModel):
    """Événement dans l'agenda du Parti."""

    class StatusChoices(models.TextChoices):
        UPCOMING = "upcoming", "À venir"
        ONGOING = "ongoing", "En cours"
        COMPLETED = "completed", "Terminé"
        CANCELLED = "cancelled", "Annulé"

    class EventTypeChoices(models.TextChoices):
        MEETING = "meeting", "Réunion"
        RALLY = "rally", "Rassemblement"
        CONFERENCE = "conference", "Conférence"
        WORKSHOP = "workshop", "Atelier"
        CEREMONY = "ceremony", "Cérémonie"
        CAMPAIGN = "campaign", "Campagne"
        OTHER = "other", "Autre"

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(
        max_length=500, blank=True, default="",
        help_text="Résumé court pour les listes.",
    )
    cover_image = models.ImageField(upload_to="events/covers/", blank=True, null=True)

    event_type = models.CharField(
        max_length=20,
        choices=EventTypeChoices.choices,
        default=EventTypeChoices.OTHER,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.UPCOMING,
        db_index=True,
    )

    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(null=True, blank=True)

    location = models.CharField(max_length=300, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    address = models.TextField(blank=True, default="")
    map_url = models.URLField(max_length=500, blank=True, default="")

    organizer = models.CharField(max_length=200, blank=True, default="")
    contact_email = models.EmailField(blank=True, default="")
    contact_phone = models.CharField(max_length=30, blank=True, default="")

    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["status", "-start_date"], name="idx_event_status_date"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def computed_status(self):
        """Calcule le statut en fonction des dates."""
        if self.status == self.StatusChoices.CANCELLED:
            return self.StatusChoices.CANCELLED
        now = timezone.now()
        if now < self.start_date:
            return self.StatusChoices.UPCOMING
        if self.end_date and now > self.end_date:
            return self.StatusChoices.COMPLETED
        return self.StatusChoices.ONGOING
