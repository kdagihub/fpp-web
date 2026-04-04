from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.api.permissions import IsAdminUser
from apps.api.serializers.bureau import AdminBureauMemberSerializer, PublicBureauMemberSerializer
from apps.site_settings.models import BureauMember


class PublicBureauListView(generics.ListAPIView):
    """Liste publique des membres actifs du Bureau National."""

    permission_classes = [AllowAny]
    serializer_class = PublicBureauMemberSerializer
    pagination_class = None

    def get_queryset(self):
        return BureauMember.objects.filter(is_active=True)


class AdminBureauListCreateView(generics.ListCreateAPIView):
    """Liste admin + création d'un membre du bureau."""

    permission_classes = [IsAdminUser]
    serializer_class = AdminBureauMemberSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = None

    def get_queryset(self):
        return BureauMember.objects.all()


class AdminBureauDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail / modification / suppression d'un membre du bureau."""

    permission_classes = [IsAdminUser]
    serializer_class = AdminBureauMemberSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return BureauMember.objects.all()

    def perform_update(self, serializer):
        clear_photo = self.request.data.get("clear_photo", "").lower() in ("true", "1")
        instance = serializer.save()
        if clear_photo and not self.request.FILES.get("photo"):
            if instance.photo:
                instance.photo.delete(save=False)
            instance.photo = None
            instance.save(update_fields=["photo"])
