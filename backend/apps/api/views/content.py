import mimetypes

from django.db.models import Count, Q
from django.http import FileResponse
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt
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
    CanManageDocuments,
    CanManageEvents,
    CanManageMedia,
    CanManageProgram,
)
from apps.api.serializers.content import (
    AdminArticleCreateSerializer,
    AdminArticleDetailSerializer,
    AdminArticleListSerializer,
    AdminCategorySerializer,
    AdminDocumentSerializer,
    AdminEventDetailSerializer,
    AdminEventListSerializer,
    AdminMediaContentSerializer,
    AdminProgramItemSerializer,
    AdminProgramSectionSerializer,
    PublicArticleDetailSerializer,
    PublicArticleListSerializer,
    PublicCategorySerializer,
    PublicDocumentSerializer,
    PublicEventDetailSerializer,
    PublicEventListSerializer,
    PublicMediaContentSerializer,
    PublicProgramSectionDetailSerializer,
    PublicProgramSectionListSerializer,
)
from apps.content.models import Article, Category, Document, Event, MediaContent, ProgramItem, ProgramSection
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
# Public — Media
# ===========================================================================

class PublicMediaContentListView(ListAPIView):
    """Contenus médias publiés (vidéos, publications Facebook/YouTube)."""

    permission_classes = [AllowAny]
    serializer_class = PublicMediaContentSerializer
    pagination_class = SmallPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["platform", "embed_type", "category"]
    search_fields = ["title", "description"]
    ordering_fields = ["published_at"]
    ordering = ["-published_at"]

    def get_queryset(self):
        qs = MediaContent.objects.filter(is_active=True)
        featured = self.request.query_params.get("featured")
        if featured == "true":
            qs = qs.filter(is_featured=True)
        return qs


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


# ===========================================================================
# Admin — Media
# ===========================================================================

class AdminMediaContentListCreateView(APIView):
    """Admin : lister et créer des contenus médias."""

    permission_classes = [IsAuthenticated, CanManageMedia]

    def get(self, request):
        qs = MediaContent.objects.all().order_by("-published_at")
        platform = request.query_params.get("platform")
        if platform:
            qs = qs.filter(platform=platform)
        serializer = AdminMediaContentSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminMediaContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="MediaContent",
            entity_id=media.pk,
            request=request,
        )

        return Response(
            AdminMediaContentSerializer(media).data,
            status=status.HTTP_201_CREATED,
        )


class AdminMediaContentDetailView(APIView):
    """Admin : modifier ou supprimer un contenu média."""

    permission_classes = [IsAuthenticated, CanManageMedia]

    def _get_media(self, pk):
        try:
            return MediaContent.objects.get(pk=pk)
        except MediaContent.DoesNotExist:
            return None

    def get(self, request, pk):
        media = self._get_media(pk)
        if not media:
            return Response({"detail": "Média introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminMediaContentSerializer(media).data)

    def patch(self, request, pk):
        media = self._get_media(pk)
        if not media:
            return Response({"detail": "Média introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminMediaContentSerializer(media, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="MediaContent",
            entity_id=media.pk,
            request=request,
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        media = self._get_media(pk)
        if not media:
            return Response({"detail": "Média introuvable."}, status=status.HTTP_404_NOT_FOUND)

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.DELETE,
            entity_type="MediaContent",
            entity_id=media.pk,
            request=request,
        )

        media.delete()
        return Response({"detail": "Média supprimé."}, status=status.HTTP_200_OK)


# ===========================================================================
# Public — Programme
# ===========================================================================

class PublicProgramSectionListView(ListAPIView):
    """Sections actives du programme avec le nombre de mesures."""

    permission_classes = [AllowAny]
    serializer_class = PublicProgramSectionListSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            ProgramSection.objects
            .filter(is_active=True)
            .annotate(item_count=Count("items", filter=Q(items__is_active=True)))
            .order_by("order", "title")
        )


class PublicProgramSectionDetailView(RetrieveAPIView):
    """Détail d'une section avec ses mesures actives."""

    permission_classes = [AllowAny]
    serializer_class = PublicProgramSectionDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return ProgramSection.objects.filter(is_active=True)


# ===========================================================================
# Public — Événements / Agenda
# ===========================================================================

class PublicEventListView(ListAPIView):
    """Événements publiés, filtrables par type et statut."""

    permission_classes = [AllowAny]
    serializer_class = PublicEventListSerializer
    pagination_class = SmallPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["event_type", "status", "city"]
    search_fields = ["title", "short_description", "location"]
    ordering_fields = ["start_date"]
    ordering = ["-start_date"]

    def get_queryset(self):
        qs = Event.objects.filter(is_active=True, published_at__isnull=False)

        featured = self.request.query_params.get("featured")
        if featured == "true":
            qs = qs.filter(is_featured=True)

        upcoming = self.request.query_params.get("upcoming")
        if upcoming == "true":
            qs = qs.filter(start_date__gte=timezone.now()).order_by("start_date")

        return qs


class PublicEventDetailView(RetrieveAPIView):
    """Détail d'un événement publié par son slug."""

    permission_classes = [AllowAny]
    serializer_class = PublicEventDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Event.objects.filter(is_active=True, published_at__isnull=False)


# ===========================================================================
# Admin — Programme
# ===========================================================================

class AdminProgramSectionListCreateView(APIView):
    """Admin : lister et créer des sections du programme."""

    permission_classes = [IsAuthenticated, CanManageProgram]

    def get(self, request):
        qs = (
            ProgramSection.objects.all()
            .annotate(item_count=Count("items"))
            .order_by("order", "title")
        )
        serializer = AdminProgramSectionSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminProgramSectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        section = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="ProgramSection",
            entity_id=section.pk,
            request=request,
        )

        return Response(
            AdminProgramSectionSerializer(section).data,
            status=status.HTTP_201_CREATED,
        )


class AdminProgramSectionDetailView(APIView):
    """Admin : détail, modification et suppression d'une section."""

    permission_classes = [IsAuthenticated, CanManageProgram]

    def _get_section(self, pk):
        try:
            return ProgramSection.objects.annotate(item_count=Count("items")).get(pk=pk)
        except ProgramSection.DoesNotExist:
            return None

    def get(self, request, pk):
        section = self._get_section(pk)
        if not section:
            return Response({"detail": "Section introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminProgramSectionSerializer(section).data)

    def patch(self, request, pk):
        section = self._get_section(pk)
        if not section:
            return Response({"detail": "Section introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminProgramSectionSerializer(section, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="ProgramSection",
            entity_id=section.pk,
            request=request,
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        section = self._get_section(pk)
        if not section:
            return Response({"detail": "Section introuvable."}, status=status.HTTP_404_NOT_FOUND)

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.DELETE,
            entity_type="ProgramSection",
            entity_id=section.pk,
            request=request,
        )

        section.delete()
        return Response({"detail": "Section supprimée."}, status=status.HTTP_200_OK)


class AdminProgramItemListCreateView(APIView):
    """Admin : lister et créer des mesures dans une section."""

    permission_classes = [IsAuthenticated, CanManageProgram]

    def get(self, request):
        qs = ProgramItem.objects.all().select_related("section").order_by("section__order", "order")
        section_id = request.query_params.get("section")
        if section_id:
            qs = qs.filter(section_id=section_id)
        serializer = AdminProgramItemSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminProgramItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="ProgramItem",
            entity_id=item.pk,
            request=request,
        )

        return Response(
            AdminProgramItemSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class AdminProgramItemDetailView(APIView):
    """Admin : modifier ou supprimer une mesure du programme."""

    permission_classes = [IsAuthenticated, CanManageProgram]

    def _get_item(self, pk):
        try:
            return ProgramItem.objects.select_related("section").get(pk=pk)
        except ProgramItem.DoesNotExist:
            return None

    def get(self, request, pk):
        item = self._get_item(pk)
        if not item:
            return Response({"detail": "Mesure introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminProgramItemSerializer(item).data)

    def patch(self, request, pk):
        item = self._get_item(pk)
        if not item:
            return Response({"detail": "Mesure introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminProgramItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="ProgramItem",
            entity_id=item.pk,
            request=request,
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        item = self._get_item(pk)
        if not item:
            return Response({"detail": "Mesure introuvable."}, status=status.HTTP_404_NOT_FOUND)

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.DELETE,
            entity_type="ProgramItem",
            entity_id=item.pk,
            request=request,
        )

        item.delete()
        return Response({"detail": "Mesure supprimée."}, status=status.HTTP_200_OK)


# ===========================================================================
# Admin — Événements / Agenda
# ===========================================================================

class AdminEventListCreateView(APIView):
    """Admin : lister et créer des événements."""

    permission_classes = [IsAuthenticated, CanManageEvents]

    def get(self, request):
        qs = Event.objects.all().order_by("-start_date")

        event_status = request.query_params.get("status")
        if event_status:
            qs = qs.filter(status=event_status)

        event_type = request.query_params.get("event_type")
        if event_type:
            qs = qs.filter(event_type=event_type)

        serializer = AdminEventListSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminEventDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="Event",
            entity_id=event.pk,
            request=request,
        )

        return Response(
            AdminEventDetailSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )


class AdminEventDetailView(APIView):
    """Admin : détail, modification et suppression d'un événement."""

    permission_classes = [IsAuthenticated, CanManageEvents]

    def _get_event(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return None

    def get(self, request, pk):
        event = self._get_event(pk)
        if not event:
            return Response({"detail": "Événement introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminEventDetailSerializer(event).data)

    def patch(self, request, pk):
        event = self._get_event(pk)
        if not event:
            return Response({"detail": "Événement introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminEventDetailSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="Event",
            entity_id=event.pk,
            request=request,
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        event = self._get_event(pk)
        if not event:
            return Response({"detail": "Événement introuvable."}, status=status.HTTP_404_NOT_FOUND)

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.DELETE,
            entity_type="Event",
            entity_id=event.pk,
            request=request,
        )

        event.delete()
        return Response({"detail": "Événement supprimé."}, status=status.HTTP_200_OK)


# ===========================================================================
# Documents — Public
# ===========================================================================

class PublicDocumentListView(ListAPIView):
    """Documents publics téléchargeables."""

    permission_classes = [AllowAny]
    serializer_class = PublicDocumentSerializer
    pagination_class = SmallPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "download_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Document.objects.filter(is_public=True).select_related("uploaded_by")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs


class PublicDocumentDownloadView(APIView):
    """Incrémente le compteur de téléchargement d'un document public."""

    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk, is_public=True)
        except Document.DoesNotExist:
            return Response({"detail": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)
        doc.download_count += 1
        doc.save(update_fields=["download_count"])
        return Response({"download_count": doc.download_count})


class PublicDocumentPreviewView(APIView):
    """Sert le fichier en ligne pour l'aperçu (iframe/object embedding).

    Exempt de X-Frame-Options pour permettre l'embedding cross-origin.
    """

    permission_classes = [AllowAny]

    @xframe_options_exempt
    def get(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk, is_public=True)
        except Document.DoesNotExist:
            return Response(
                {"detail": "Document introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not doc.file:
            return Response(
                {"detail": "Aucun fichier attaché."},
                status=status.HTTP_404_NOT_FOUND,
            )

        content_type, _ = mimetypes.guess_type(doc.file.name)
        if not content_type:
            content_type = "application/octet-stream"

        response = FileResponse(
            doc.file.open("rb"),
            content_type=content_type,
        )
        response["Content-Disposition"] = "inline"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class AdminDocumentPreviewView(APIView):
    """Sert un document (public ou privé) pour l'aperçu admin."""

    permission_classes = [IsAuthenticated, CanManageDocuments]

    @xframe_options_exempt
    def get(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                {"detail": "Document introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not doc.file:
            return Response(
                {"detail": "Aucun fichier attaché."},
                status=status.HTTP_404_NOT_FOUND,
            )

        content_type, _ = mimetypes.guess_type(doc.file.name)
        if not content_type:
            content_type = "application/octet-stream"

        response = FileResponse(
            doc.file.open("rb"),
            content_type=content_type,
        )
        response["Content-Disposition"] = "inline"
        response["X-Content-Type-Options"] = "nosniff"
        return response


# ===========================================================================
# Documents — Admin
# ===========================================================================

class AdminDocumentListCreateView(APIView):
    """Admin : liste et création de documents."""

    permission_classes = [IsAuthenticated, CanManageDocuments]

    def get(self, request):
        qs = Document.objects.select_related("uploaded_by").all()
        category = request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        is_public = request.query_params.get("is_public")
        if is_public is not None:
            qs = qs.filter(is_public=is_public.lower() == "true")
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        serializer = AdminDocumentSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminDocumentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        doc = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="Document",
            entity_id=doc.pk,
            request=request,
        )

        return Response(
            AdminDocumentSerializer(doc, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminDocumentDetailView(APIView):
    """Admin : détail, modification et suppression d'un document."""

    permission_classes = [IsAuthenticated, CanManageDocuments]

    def _get_doc(self, pk):
        try:
            return Document.objects.select_related("uploaded_by").get(pk=pk)
        except Document.DoesNotExist:
            return None

    def get(self, request, pk):
        doc = self._get_doc(pk)
        if not doc:
            return Response({"detail": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdminDocumentSerializer(doc, context={"request": request}).data)

    def patch(self, request, pk):
        doc = self._get_doc(pk)
        if not doc:
            return Response({"detail": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminDocumentSerializer(doc, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="Document",
            entity_id=doc.pk,
            request=request,
        )

        return Response(serializer.data)

    def delete(self, request, pk):
        doc = self._get_doc(pk)
        if not doc:
            return Response({"detail": "Document introuvable."}, status=status.HTTP_404_NOT_FOUND)

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.DELETE,
            entity_type="Document",
            entity_id=doc.pk,
            request=request,
        )

        if doc.file:
            doc.file.delete(save=False)
        doc.delete()
        return Response({"detail": "Document supprimé."}, status=status.HTTP_200_OK)
