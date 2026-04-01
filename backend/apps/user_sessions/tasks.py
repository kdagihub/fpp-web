import logging
from datetime import timedelta

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_sessions():
    """
    Ferme les UserSession inactives depuis plus de 24h.
    Tâche périodique : quotidienne à 3h.
    """
    from django.utils import timezone
    from apps.user_sessions.models import UserSession

    cutoff = timezone.now() - timedelta(hours=24)
    expired = UserSession.objects.filter(
        is_active=True,
        last_activity__lt=cutoff,
    )
    count = expired.count()
    expired.update(is_active=False, ended_at=timezone.now())
    if count:
        logger.info("Fermé %d session(s) inactive(s) depuis >24h", count)
