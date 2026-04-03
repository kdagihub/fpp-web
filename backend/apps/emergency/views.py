import logging

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.throttle import EmergencyThrottle
from apps.emergency.utils import (
    CONFIRMATION_TEXT,
    create_emergency_superuser,
    create_encrypted_zip,
    export_dumpdata,
    export_users_excel,
    purge_sensitive_data,
    send_emergency_emails,
    verify_code,
)

logger = logging.getLogger(__name__)


class IsEmergencyUser(IsAuthenticated):
    """Seuls les utilisateurs marqués is_emergency_user peuvent accéder."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return getattr(request.user, "is_emergency_user", False)


class EmergencyPurgeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)
    confirmation = serializers.CharField(max_length=50)

    def validate_confirmation(self, value):
        if value != CONFIRMATION_TEXT:
            raise serializers.ValidationError(
                f"Vous devez taper exactement « {CONFIRMATION_TEXT} »."
            )
        return value


class EmergencyPurgeView(APIView):
    """POST /api/emergency/purge/ — Déclenche la procédure de purge d'urgence."""

    permission_classes = [IsEmergencyUser]
    throttle_classes = [EmergencyThrottle]

    def post(self, request):
        serializer = EmergencyPurgeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        # 1. Vérifier le code
        if not verify_code(code):
            return Response(
                {"detail": "Code d'urgence invalide ou expiré."},
                status=status.HTTP_403_FORBIDDEN,
            )

        logger.critical(
            "PROCÉDURE D'URGENCE déclenchée par %s (%s)",
            request.user.email,
            request.user.id,
        )

        try:
            # 2. Export Excel
            excel_buf = export_users_excel()
            logger.info("Export Excel terminé.")

            # 3. Export JSON (dumpdata)
            json_bytes = export_dumpdata()
            logger.info("Dump JSON terminé.")

            # 4. Chiffrement ZIP
            zip_buf = create_encrypted_zip(code, excel_buf, json_bytes)
            logger.info("ZIP chiffré créé.")

            # 5. Envoi emails
            sent = send_emergency_emails(zip_buf)
            if sent == 0:
                return Response(
                    {"detail": "Aucun email n'a pu être envoyé. Purge annulée."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            logger.info("%d email(s) d'urgence envoyé(s).", sent)

            # 6. Purge des données sensibles
            purge_sensitive_data()
            logger.info("Tables sensibles purgées.")

            # 7. Recréation du superuser
            su_info = create_emergency_superuser()
            logger.info("Superuser d'urgence créé : %s", su_info["email"])

        except Exception:
            logger.exception("Erreur fatale durant la procédure d'urgence.")
            return Response(
                {"detail": "Une erreur est survenue durant la procédure."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"status": "purged"}, status=status.HTTP_200_OK)
