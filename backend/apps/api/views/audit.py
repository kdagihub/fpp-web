from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.api.pagination import StandardPagination
from apps.api.permissions import CanViewAuditLog
from apps.core.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", default="")
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id", "user", "user_email", "user_full_name",
            "action", "entity_type", "entity_id",
            "changes", "ip_address", "user_agent",
            "created_at",
        ]

    def get_user_full_name(self, obj):
        if obj.user:
            return obj.user.full_name
        return ""


class AdminAuditLogView(ListAPIView):
    """Admin : journal d'audit pagine et filtrable."""

    permission_classes = [IsAuthenticated, CanViewAuditLog]
    serializer_class = AuditLogSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["action", "entity_type", "user"]
    search_fields = ["entity_type", "user__email", "user__first_name", "user__last_name"]
    ordering_fields = ["created_at", "action"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return AuditLog.objects.select_related("user")
