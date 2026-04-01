import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def log_audit_async(user_id, action, entity_type, entity_id, changes=None, ip_address=None, user_agent=""):
    """Écriture asynchrone dans l'AuditLog (décharge les vues)."""
    from apps.core.models import AuditLog

    AuditLog.objects.create(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@shared_task
def flush_expired_blacklisted_tokens():
    """
    Purge les tokens expirés de la table token_blacklist.
    Les OutstandingToken dont le refresh est expiré n'ont plus d'utilité.
    Tâche périodique : quotidienne à 4h.
    """
    from django.utils import timezone
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

    expired = OutstandingToken.objects.filter(expires_at__lt=timezone.now())
    count = expired.count()
    expired.delete()
    if count:
        logger.info("Purgé %d token(s) expiré(s) de la blacklist", count)
