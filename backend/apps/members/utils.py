import hashlib
import hmac

from django.conf import settings
from django.db import transaction


def generate_hmac_matricule(user, city):
    """
    Génère un matricule HMAC opaque et non devinable.
    Appelé uniquement quand l'admin valide l'adhésion.

    Format : FPP-XXXX-XXXX-XXXX (12 hex uppercase après préfixe)
    """
    from apps.members.models import MemberProfile

    with transaction.atomic():
        seq = MemberProfile.objects.select_for_update().filter(
            matricule__isnull=False,
        ).count() + 1

    payload = f"{user.pk}:{user.date_of_birth}:{city}:{seq}"
    digest = hmac.new(
        settings.MATRICULE_SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()[:12].upper()

    return f"FPP-{digest[:4]}-{digest[4:8]}-{digest[8:]}"
