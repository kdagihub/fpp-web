from django.core.cache import cache
from django.utils import timezone


class SessionActivityMiddleware:
    """
    Met à jour last_activity sur la UserSession active à chaque requête authentifiée.
    Throttlé à 1 update par minute par user pour ne pas surcharger la DB.
    """

    THROTTLE_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(request, "user") and request.user.is_authenticated:
            self._throttled_update(request.user)

        return response

    @classmethod
    def _throttled_update(cls, user):
        cache_key = f"session_activity:{user.pk}"
        if cache.get(cache_key):
            return

        from apps.user_sessions.models import UserSession

        UserSession.objects.filter(
            user=user,
            is_active=True,
        ).update(last_activity=timezone.now())

        cache.set(cache_key, True, cls.THROTTLE_SECONDS)
