import csv

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.pagination import StandardPagination
from apps.api.permissions import CanExportContacts, CanManageContacts
from apps.api.serializers.contact import (
    AdminContactDetailSerializer,
    AdminContactListSerializer,
    PublicContactSerializer,
)
from apps.api.throttle import AnonBurstThrottle
from apps.contact.models import ContactMessage
from apps.core.mixins import AuditMixin
from apps.core.models import AuditLog


# ===========================================================================
# Public
# ===========================================================================

class PublicContactView(APIView):
    """Envoyer un message de contact (public, throttled)."""

    permission_classes = [AllowAny]
    throttle_classes = [AnonBurstThrottle]

    def post(self, request):
        serializer = PublicContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        from apps.accounts.tasks import notify_contact_message, send_contact_acknowledgment
        notify_contact_message.delay(str(instance.pk))
        if instance.email:
            send_contact_acknowledgment.delay(str(instance.pk))

        return Response(
            {"detail": "Votre message a été envoyé. Nous vous répondrons dans les plus brefs délais."},
            status=status.HTTP_201_CREATED,
        )


# ===========================================================================
# Admin
# ===========================================================================

class AdminContactListView(ListAPIView):
    """Admin : liste paginee des messages de contact."""

    permission_classes = [IsAuthenticated, CanManageContacts]
    serializer_class = AdminContactListSerializer
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "email", "subject"]
    ordering_fields = ["created_at", "is_read"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = ContactMessage.objects.all()
        is_read = self.request.query_params.get("is_read")
        if is_read == "true":
            qs = qs.filter(is_read=True)
        elif is_read == "false":
            qs = qs.filter(is_read=False)
        return qs


class AdminContactDetailView(APIView):
    """Admin : detail d'un message + marquage comme lu."""

    permission_classes = [IsAuthenticated, CanManageContacts]

    def get(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
        except ContactMessage.DoesNotExist:
            return Response({"detail": "Message introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save(update_fields=["is_read", "read_at", "updated_at"])

        return Response(AdminContactDetailSerializer(message).data)

    def patch(self, request, pk):
        """Permet de re-marquer un message comme non lu."""
        try:
            message = ContactMessage.objects.get(pk=pk)
        except ContactMessage.DoesNotExist:
            return Response({"detail": "Message introuvable."}, status=status.HTTP_404_NOT_FOUND)

        is_read = request.data.get("is_read")
        if is_read is not None:
            message.is_read = bool(is_read)
            message.read_at = timezone.now() if message.is_read else None
            message.save(update_fields=["is_read", "read_at", "updated_at"])

        return Response(AdminContactDetailSerializer(message).data)


class AdminContactExportView(APIView):
    """Admin : export CSV des messages de contact."""

    permission_classes = [IsAuthenticated, CanExportContacts]

    def get(self, request):
        messages = ContactMessage.objects.all().order_by("-created_at")

        is_read = request.query_params.get("is_read")
        if is_read == "true":
            messages = messages.filter(is_read=True)
        elif is_read == "false":
            messages = messages.filter(is_read=False)

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="contacts_fpp.csv"'
        response.write("\ufeff")

        writer = csv.writer(response, delimiter=";")
        writer.writerow(["Nom", "Email", "Téléphone", "Sujet", "Message", "Lu", "Date"])

        for msg in messages:
            writer.writerow([
                msg.name,
                msg.email,
                msg.phone,
                msg.subject,
                msg.message,
                "Oui" if msg.is_read else "Non",
                msg.created_at.strftime("%d/%m/%Y %H:%M"),
            ])

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.EXPORT,
            entity_type="ContactMessage",
            entity_id=request.user.pk,
            changes={"count": messages.count()},
            request=request,
        )

        return response
