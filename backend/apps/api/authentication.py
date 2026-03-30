from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Lit le JWT depuis le cookie httpOnly 'access_token' au lieu du header Authorization.
    Fallback sur le header Authorization si le cookie n'est pas présent (utile pour les tests).
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT.get("AUTH_COOKIE", "access_token"))

        if raw_token is None:
            return super().authenticate(request)

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
