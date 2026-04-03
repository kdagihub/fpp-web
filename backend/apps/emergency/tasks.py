import hashlib
import logging
import secrets
import string

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

CODE_LENGTH = 12
CODE_TTL = 86_400  # 24 h
CACHE_KEY_PREFIX = "emergency:code:"


def _generate_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(CODE_LENGTH))


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


@shared_task(name="apps.emergency.tasks.rotate_emergency_codes")
def rotate_emergency_codes() -> dict:
    """Génère un code unique par email d'urgence, stocke le hash dans le cache
    Redis (TTL 24 h) et envoie le code en clair par email."""

    emails: list[str] = getattr(settings, "EMERGENCY_EMAILS", [])
    if not emails:
        logger.warning("EMERGENCY_EMAILS est vide — aucun code généré.")
        return {"sent": 0}

    sent = 0
    for email in emails:
        code = _generate_code()
        hashed = _hash_code(code)
        cache_key = f"{CACHE_KEY_PREFIX}{email}"
        cache.set(cache_key, hashed, timeout=CODE_TTL)

        try:
            send_mail(
                subject="[FPP] Code d'urgence — valable 24 h",
                message=(
                    f"Votre code d'urgence pour la procédure de purge :\n\n"
                    f"    {code}\n\n"
                    f"Ce code est strictement personnel et expire dans 24 heures.\n"
                    f"Ne le communiquez à personne.\n\n"
                    f"— Système de sécurité FPP"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            sent += 1
            logger.info("Code d'urgence envoyé à %s", email)
        except Exception:
            logger.exception("Échec d'envoi du code d'urgence à %s", email)

    return {"sent": sent, "total": len(emails)}
