from django.utils import timezone


class SessionActivityMiddleware:
    """Met à jour last_activity sur la UserSession active à chaque requête authentifiée."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(request, "user") and request.user.is_authenticated:
            self._update_session_activity(request.user)

        return response

    @staticmethod
    def _update_session_activity(user):
        from apps.user_sessions.models import UserSession

        UserSession.objects.filter(
            user=user,
            is_active=True,
        ).update(last_activity=timezone.now())
