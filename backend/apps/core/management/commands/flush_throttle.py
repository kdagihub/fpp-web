"""
Commande pour vider le cache de throttle (rate limiting).
Usage : python manage.py flush_throttle
"""

from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Vide le cache de throttle DRF (résout les erreurs 429 bloquantes)"

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write(self.style.SUCCESS(
            "Cache de throttle vidé avec succès. "
            "Les limites de requêtes ont été réinitialisées pour tous les utilisateurs."
        ))
