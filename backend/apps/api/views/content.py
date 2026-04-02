from django.db.models import Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.pagination import SmallPagination, StandardPagination
from apps.api.permissions import (
    CanCreateArticle,
    CanDeleteArticle,
    CanEditArticle,
    CanManageCategories,
)
from apps.api.serializers.content import (
    AdminArticleCreateSerializer,
    AdminArticleDetailSerializer,
    AdminArticleListSerializer,
    AdminCategorySerializer,
    PublicArticleDetailSerializer,
    PublicArticleListSerializer,
    PublicCategorySerializer,
)
from apps.content.models import Article, Category
from apps.core.mixins import AuditMixin
from apps.core.models import AuditLog


# ===========================================================================
# Public
# ===========================================================================

class PublicArticleListView(ListAPIView):
    """Articles publies, pagines, filtrables par categorie."""

    permission_classes = [AllowAny]
    serializer_class = PublicArticleListSerializer
    pagination_class = SmallPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "summary"]
    ordering_fields = ["published_at"]
    ordering = ["-published_at"]

    def get_queryset(self):
        qs = (
            Article.objects
            .filter(status=Article.StatusChoices.PUBLISHED, deleted_at__isnull=True)
            .select_related("author", "category")
        )
        category_slug = self.request.query_params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug, category__is_active=True)

        featured = self.request.query_params.get("featured")
        if featured == "true":
            qs = qs.filter(is_featured=True)

        return qs


class PublicArticleDetailView(RetrieveAPIView):
    """Detail d'un article publie par son slug."""

    permission_classes = [AllowAny]
    serializer_class = PublicArticleDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Article.objects
            .filter(status=Article.StatusChoices.PUBLISHED, deleted_at__isnull=True)
            .select_related("author", "category")
        )


class PublicCategoryListView(ListAPIView):
    """Categories actives avec nombre d'articles publies."""

    permission_classes = [AllowAny]
    serializer_class = PublicCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Category.objects
            .filter(is_active=True)
            .annotate(article_count=Count(
                "articles",
                filter=Q(
                    articles__status=Article.StatusChoices.PUBLISHED,
                    articles__deleted_at__isnull=True,
                ),
            ))
            .order_by("name")
        )


class PublicStatsView(APIView):
    """Stats publiques : nombre de membres valides, articles publies, etc."""

    permission_classes = [AllowAny]

    def get(self, request):
        from apps.members.models import MemberProfile

        stats = {
            "total_members": MemberProfile.objects.filter(
                membership_status=MemberProfile.StatusChoices.VALIDATED,
            ).count(),
            "total_articles": Article.objects.filter(
                status=Article.StatusChoices.PUBLISHED,
                deleted_at__isnull=True,
            ).count(),
            "total_categories": Category.objects.filter(is_active=True).count(),
        }
        return Response(stats)


# ===========================================================================
# Admin — Articles
# ===========================================================================

class AdminArticleListView(ListAPIView):
    """Admin : tous les articles (y compris brouillons et archives)."""

    permission_classes = [IsAuthenticated, CanCreateArticle]
    serializer_class = AdminArticleListSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "category", "is_featured"]
    search_fields = ["title", "summary"]
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Article.objects
            .filter(deleted_at__isnull=True)
            .select_related("author", "category")
        )


class AdminArticleCreateView(APIView):
    """Admin : creer un article."""

    permission_classes = [IsAuthenticated, CanCreateArticle]

    def post(self, request):
        serializer = AdminArticleCreateSerializer(
            data=request.data, context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        article = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="Article",
            entity_id=article.pk,
            request=request,
        )

        return Response(
            AdminArticleDetailSerializer(article).data,
            status=status.HTTP_201_CREATED,
        )


class AdminArticleDetailView(APIView):
    """Admin : detail, modification et suppression (soft) d'un article."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), CanCreateArticle()]
        if self.request.method == "PATCH":
            return [IsAuthenticated(), CanEditArticle()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), CanDeleteArticle()]
        return [IsAuthenticated()]

    def _get_article(self, pk):
        try:
            return (
                Article.objects
                .filter(deleted_at__isnull=True)
                .select_related("author", "category")
                .get(pk=pk)
            )
        except Article.DoesNotExist:
            return None

    def get(self, request, pk):
        article = self._get_article(pk)
        if not article:
            return Response({"detail": "Article introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminArticleDetailSerializer(article).data)

    def patch(self, request, pk):
        article = self._get_article(pk)
        if not article:
            return Response({"detail": "Article introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminArticleCreateSerializer(
            article, data=request.data, partial=True, context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        old_values = {
            field: getattr(article, field)
            for field in request.data.keys()
            if hasattr(article, field) and field != "cover_image"
        }

        article = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="Article",
            entity_id=article.pk,
            changes={k: {"old": str(v), "new": str(getattr(article, k))} for k, v in old_values.items()},
            request=request,
        )

        article.refresh_from_db()
        return Response(AdminArticleDetailSerializer(
            Article.objects.select_related("author", "category").get(pk=article.pk)
        ).data)

    def delete(self, request, pk):
        article = self._get_article(pk)
        if not article:
            return Response({"detail": "Article introuvable."}, status=status.HTTP_404_NOT_FOUND)

        article.deleted_at = timezone.now()
        article.save(update_fields=["deleted_at", "updated_at"])

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.DELETE,
            entity_type="Article",
            entity_id=article.pk,
            request=request,
        )

        return Response({"detail": "Article supprimé."}, status=status.HTTP_200_OK)


# ===========================================================================
# Admin — Categories
# ===========================================================================

class AdminCategoryListCreateView(APIView):
    """Admin : lister et creer des categories."""

    permission_classes = [IsAuthenticated, CanManageCategories]

    def get(self, request):
        categories = (
            Category.objects
            .annotate(article_count=Count(
                "articles",
                filter=Q(articles__deleted_at__isnull=True),
            ))
            .order_by("name")
        )
        serializer = AdminCategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="Category",
            entity_id=category.pk,
            request=request,
        )

        return Response(
            AdminCategorySerializer(category).data,
            status=status.HTTP_201_CREATED,
        )


class AdminCategoryDetailView(APIView):
    """Admin : modifier ou supprimer une categorie."""

    permission_classes = [IsAuthenticated, CanManageCategories]

    def _get_category(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def patch(self, request, pk):
        category = self._get_category(pk)
        if not category:
            return Response({"detail": "Catégorie introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminCategorySerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="Category",
            entity_id=category.pk,
            request=request,
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        category = self._get_category(pk)
        if not category:
            return Response({"detail": "Catégorie introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if category.articles.filter(deleted_at__isnull=True).exists():
            return Response(
                {"detail": "Impossible de supprimer une catégorie contenant des articles."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.DELETE,
            entity_type="Category",
            entity_id=category.pk,
            request=request,
        )

        category.delete()
        return Response({"detail": "Catégorie supprimée."}, status=status.HTTP_200_OK)
