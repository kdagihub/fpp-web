from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers

from apps.content.models import Article, Category
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
        read_only_fields = ["id", "slug", "author_name", "category_name", "deleted_at", "created_at", "updated_at"]


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
        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        if old_status != Article.StatusChoices.PUBLISHED and new_status == Article.StatusChoices.PUBLISHED:
            validated_data["published_at"] = timezone.now()

        return super().update(instance, validated_data)
