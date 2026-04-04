from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import IsAdminUser
from apps.api.serializers.membership import (
    MembershipDetailSerializer,
    MembershipRequestSerializer,
    VerifyMatriculeResultSerializer,
    VerifyMatriculeSerializer,
)
from apps.core.mixins import AuditMixin
from apps.core.models import AuditLog
from apps.members.models import MemberProfile
from apps.members.utils import generate_hmac_matricule


class MembershipRequestView(APIView):
    """Demande d'adhésion (Phase 2) et consultation du statut."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retourne le statut de la demande d'adhésion du user connecté."""
        try:
            profile = request.user.member_profile
        except MemberProfile.DoesNotExist:
            return Response(
                {"detail": "Aucune demande d'adhésion soumise.", "membership": None},
            )
        serializer = MembershipDetailSerializer(profile)
        return Response({"membership": serializer.data})

    def post(self, request):
        """Soumet une demande d'adhésion (crée MemberProfile status=pending)."""
        serializer = MembershipRequestSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="MemberProfile",
            entity_id=profile.pk,
            request=request,
        )

        from apps.accounts.tasks import notify_party_membership_request
        notify_party_membership_request.delay(str(request.user.pk))

        return Response(
            {"detail": "Demande d'adhésion soumise. Elle sera examinée par un administrateur."},
            status=status.HTTP_201_CREATED,
        )


class ValidateMembershipView(APIView):
    """Admin : valider ou rejeter une demande d'adhésion."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        """Valide l'adhésion : génère le matricule HMAC et passe status=validated."""
        try:
            profile = MemberProfile.objects.select_related("user").get(pk=pk)
        except MemberProfile.DoesNotExist:
            return Response(
                {"detail": "Profil membre introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if profile.membership_status != MemberProfile.StatusChoices.PENDING:
            return Response(
                {"detail": f"Cette demande est déjà '{profile.get_membership_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = request.data.get("action")
        if action not in ("validate", "reject"):
            return Response(
                {"detail": "Action requise : 'validate' ou 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if action == "validate":
                profile.matricule = generate_hmac_matricule(profile.user, profile.city)
                profile.membership_status = MemberProfile.StatusChoices.VALIDATED
                profile.membership_date = timezone.now()
                profile.save(update_fields=["matricule", "membership_status", "membership_date", "updated_at"])

                AuditMixin.log_action(
                    user=request.user,
                    action=AuditLog.ActionChoices.UPDATE,
                    entity_type="MemberProfile",
                    entity_id=profile.pk,
                    changes={"membership_status": "validated", "matricule": profile.matricule},
                    request=request,
                )

                return Response({
                    "detail": "Adhésion validée.",
                    "matricule": profile.matricule,
                })

            else:
                reason = request.data.get("reason", "")
                profile.membership_status = MemberProfile.StatusChoices.REJECTED
                profile.save(update_fields=["membership_status", "updated_at"])

                AuditMixin.log_action(
                    user=request.user,
                    action=AuditLog.ActionChoices.UPDATE,
                    entity_type="MemberProfile",
                    entity_id=profile.pk,
                    changes={"membership_status": "rejected", "reason": reason},
                    request=request,
                )

                return Response({"detail": "Adhésion rejetée."})


class VerifyMatriculeView(APIView):
    """Admin : vérification d'un matricule — retourne toutes les infos du membre."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = VerifyMatriculeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        matricule = serializer.validated_data["matricule"]
        try:
            profile = MemberProfile.objects.select_related("user").get(matricule=matricule)
        except MemberProfile.DoesNotExist:
            return Response(
                {"detail": "Aucun membre trouvé avec ce matricule."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = VerifyMatriculeResultSerializer(profile)
        return Response(result.data)
