import re
from urllib.parse import parse_qs, urlparse

from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers

from apps.content.models import Article, Category, Document, Event, MediaContent, ProgramItem, ProgramSection
from apps.api.serializers.membership import validate_image_file


# ---------------------------------------------------------------------------
# Public serializers
# ---------------------------------------------------------------------------

class PublicCategorySerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "article_count"]


class PublicArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", default="")
    category_name = serializers.CharField(source="category.name", default="")
    category_slug = serializers.CharField(source="category.slug", default="")

    class Meta:
        model = Article
        fields = [
            "id", "title", "slug", "summary", "cover_image",
            "author_name", "category_name", "category_slug",
            "is_featured", "published_at",
        ]


class PublicArticleDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", default="")
    category_name = serializers.CharField(source="category.name", default="")
    category_slug = serializers.CharField(source="category.slug", default="")

    class Meta:
        model = Article
        fields = [
            "id", "title", "slug", "summary", "content", "cover_image",
            "author_name", "category_name", "category_slug",
            "is_featured", "published_at", "created_at",
        ]


# ---------------------------------------------------------------------------
# Public — MediaContent
# ---------------------------------------------------------------------------

class PublicMediaContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaContent
        fields = [
            "id", "title", "description", "platform", "embed_type",
            "source_url", "category", "is_featured", "published_at",
        ]


# ---------------------------------------------------------------------------
# Admin serializers
# ---------------------------------------------------------------------------

class AdminCategorySerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "is_active", "article_count", "created_at"]
        read_only_fields = ["id", "slug", "article_count", "created_at"]

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)


class AdminArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", default="")
    category_name = serializers.CharField(source="category.name", default="")

    class Meta:
        model = Article
        fields = [
            "id", "title", "slug", "summary", "cover_image", "status",
            "author_name", "category_name",
            "is_featured", "published_at", "created_at",
        ]


class AdminArticleDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", default="", read_only=True)
    category_name = serializers.CharField(source="category.name", default="", read_only=True)

    class Meta:
        model = Article
        fields = [
            "id", "title", "slug", "summary", "content", "cover_image", "status",
            "author", "author_name", "category", "category_name",
            "is_featured", "published_at", "deleted_at", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "slug", "author", "author_name", "category_name",
            "deleted_at", "created_at", "updated_at",
        ]


class AdminArticleCreateSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Article
        fields = [
            "title", "summary", "content", "cover_image",
            "status", "category", "is_featured",
        ]

    def validate_cover_image(self, value):
        if value:
            return validate_image_file(value, "Image de couverture")
        return value

    def validate_is_featured(self, value):
        if value:
            featured_count = Article.objects.filter(
                is_featured=True, deleted_at__isnull=True,
            ).exclude(pk=self.instance.pk if self.instance else None).count()
            if featured_count >= 3:
                raise serializers.ValidationError(
                    "Maximum 3 articles mis en avant simultanément."
                )
        return value

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        slug = slugify(validated_data["title"])
        base_slug = slug
        counter = 1
        while Article.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        validated_data["slug"] = slug

        if validated_data.get("status") == Article.StatusChoices.PUBLISHED:
            validated_data["published_at"] = timezone.now()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not instance.author:
            validated_data["author"] = self.context["request"].user

        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        if old_status != Article.StatusChoices.PUBLISHED and new_status == Article.StatusChoices.PUBLISHED:
            validated_data["published_at"] = timezone.now()

        return super().update(instance, validated_data)


# ---------------------------------------------------------------------------
# Admin — MediaContent
# ---------------------------------------------------------------------------

def _resolve_facebook_share_url(url: str) -> str:
    """Résout les URLs raccourcies Facebook /share/v/, /share/p/ et fb.watch vers l'URL réelle."""
    import re
    import requests
    from urllib.parse import urlparse, urlunparse

    lower = url.lower()
    needs_resolve = (
        "/share/v/" in lower
        or "/share/r/" in lower
        or "/share/p/" in lower
        or "fb.watch" in lower
    )
    if not needs_resolve:
        return url
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        if resp.url and resp.url != url:
            parsed = urlparse(resp.url)
            clean_url = urlunparse(parsed._replace(query="", fragment=""))
            if clean_url.endswith("/"):
                return clean_url
            return clean_url + "/"
    except Exception:
        pass
    return url


def _detect_platform(url: str):
    """Détecte automatiquement la plateforme et le type d'embed depuis une URL brute ou embed."""
    lower = url.lower()

    if "facebook.com" in lower or "fb.watch" in lower:
        platform = "facebook"
        if "plugins/post.php" in lower:
            embed_type = "post"
        elif "/share/p/" in lower or "/posts/" in lower or "plugins/post" in lower:
            embed_type = "post"
        elif "/reel/" in lower or "/share/v/" in lower or "/share/r/" in lower or "/videos/" in lower:
            embed_type = "video"
        else:
            embed_type = "video"
        return platform, embed_type

    if "youtube.com" in lower or "youtu.be" in lower:
        return "youtube", "video"

    return None, None


class AdminMediaContentSerializer(serializers.ModelSerializer):
    platform = serializers.ChoiceField(
        choices=MediaContent.PlatformChoices.choices,
        required=False, allow_blank=True,
    )
    embed_type = serializers.ChoiceField(
        choices=MediaContent.EmbedTypeChoices.choices,
        required=False, allow_blank=True,
    )

    class Meta:
        model = MediaContent
        fields = [
            "id", "title", "description", "platform", "embed_type",
            "source_url", "category", "is_featured", "is_active",
            "published_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_source_url(self, value):
        platform, _ = _detect_platform(value)
        if platform is None:
            raise serializers.ValidationError(
                "URL non reconnue. Seuls les liens Facebook et YouTube sont acceptés."
            )
        if platform == "facebook":
            value = _resolve_facebook_share_url(value)
        return value

    def _auto_fill_platform(self, validated_data):
        """Auto-détecte platform/embed_type depuis l'URL si non fournis."""
        url = validated_data.get("source_url", "")
        platform, embed_type = _detect_platform(url)
        if not validated_data.get("platform") and platform:
            validated_data["platform"] = platform
        if not validated_data.get("embed_type") and embed_type:
            validated_data["embed_type"] = embed_type

    def create(self, validated_data):
        self._auto_fill_platform(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "source_url" in validated_data:
            self._auto_fill_platform(validated_data)
        return super().update(instance, validated_data)


# ===========================================================================
# Public — Programme
# ===========================================================================

class PublicProgramItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramItem
        fields = ["id", "title", "description", "order"]


class PublicProgramSectionListSerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProgramSection
        fields = ["id", "title", "slug", "description", "icon", "cover_image", "order", "item_count"]


class PublicProgramSectionDetailSerializer(serializers.ModelSerializer):
    items = PublicProgramItemSerializer(many=True, read_only=True, source="active_items")

    class Meta:
        model = ProgramSection
        fields = ["id", "title", "slug", "description", "icon", "cover_image", "order", "items"]


# ===========================================================================
# Public — Événements / Agenda
# ===========================================================================

class PublicEventListSerializer(serializers.ModelSerializer):
    computed_status = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "slug", "short_description", "cover_image",
            "event_type", "status", "computed_status",
            "start_date", "end_date",
            "location", "city",
            "is_featured", "published_at",
        ]


class PublicEventDetailSerializer(serializers.ModelSerializer):
    computed_status = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "slug", "description", "short_description", "cover_image",
            "event_type", "status", "computed_status",
            "start_date", "end_date",
            "location", "city", "address", "map_url",
            "organizer", "contact_email", "contact_phone",
            "is_featured", "published_at", "created_at",
        ]


# ===========================================================================
# Admin — Programme
# ===========================================================================

class AdminProgramItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramItem
        fields = ["id", "section", "title", "description", "order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminProgramSectionSerializer(serializers.ModelSerializer):
    items = AdminProgramItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProgramSection
        fields = [
            "id", "title", "slug", "description", "icon", "cover_image",
            "order", "is_active", "item_count", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "item_count", "items", "created_at", "updated_at"]

    def validate_cover_image(self, value):
        if value:
            return validate_image_file(value, "Image de section")
        return value

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["title"])
        return super().create(validated_data)


# ===========================================================================
# Admin — Événements / Agenda
# ===========================================================================

class AdminEventListSerializer(serializers.ModelSerializer):
    computed_status = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "slug", "event_type", "status", "computed_status",
            "start_date", "end_date", "city", "location",
            "is_featured", "is_active", "published_at", "created_at",
        ]


class AdminEventDetailSerializer(serializers.ModelSerializer):
    computed_status = serializers.CharField(read_only=True)
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Event
        fields = [
            "id", "title", "slug", "description", "short_description", "cover_image",
            "event_type", "status", "computed_status",
            "start_date", "end_date",
            "location", "city", "address", "map_url",
            "organizer", "contact_email", "contact_phone",
            "is_featured", "is_active", "published_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "computed_status", "created_at", "updated_at"]

    def validate_cover_image(self, value):
        if value:
            return validate_image_file(value, "Image de couverture")
        return value

    def create(self, validated_data):
        slug = slugify(validated_data["title"])
        base_slug = slug
        counter = 1
        while Event.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        validated_data["slug"] = slug

        if not validated_data.get("published_at") and validated_data.get("status") != Event.StatusChoices.CANCELLED:
            validated_data["published_at"] = timezone.now()

        return super().create(validated_data)


# ===========================================================================
# Documents
# ===========================================================================

class PublicDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id", "title", "description", "category", "file_url",
            "file_size", "download_count", "uploaded_by_name", "created_at",
        ]

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else ""

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return ""


class AdminDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id", "title", "description", "file", "file_url", "category",
            "is_public", "uploaded_by", "uploaded_by_name",
            "file_size", "download_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uploaded_by", "file_size", "download_count", "created_at", "updated_at"]

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else ""

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return ""

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        instance = super().create(validated_data)
        if instance.file:
            try:
                instance.file_size = instance.file.size
                instance.save(update_fields=["file_size"])
            except Exception:
                pass
        return instance
