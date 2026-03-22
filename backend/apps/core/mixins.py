from apps.core.models import AuditLog


class AuditMixin:
    """Mixin pour enregistrer automatiquement les actions dans l'AuditLog."""

    @staticmethod
    def log_action(user, action, entity_type, entity_id, changes=None, request=None):
        ip_address = None
        user_agent = ""

        if request:
            ip_address = AuditMixin._get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]

        AuditLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
