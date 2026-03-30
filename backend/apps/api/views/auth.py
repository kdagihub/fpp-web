from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from apps.api.serializers.auth import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)
from apps.api.throttle import LoginThrottle, RegisterThrottle
from apps.api.utils import delete_jwt_cookies, get_client_ip, set_jwt_cookies
from apps.core.mixins import AuditMixin
from apps.core.models import AuditLog
from apps.user_sessions.models import UserSession


def _create_session(user, request, refresh_token):
    """Crée une UserSession lors du login."""
    from user_agents import parse as parse_ua

    ip = get_client_ip(request)
    ua_string = request.META.get("HTTP_USER_AGENT", "")
    ua = parse_ua(ua_string)

    device_str = f"{ua.browser.family} {ua.browser.version_string} / {ua.os.family} {ua.os.version_string}".strip()
    if ua.is_mobile:
        device_type = UserSession.DeviceTypeChoices.MOBILE
    elif ua.is_tablet:
        device_type = UserSession.DeviceTypeChoices.TABLET
    elif ua.is_pc:
        device_type = UserSession.DeviceTypeChoices.DESKTOP
    else:
        device_type = UserSession.DeviceTypeChoices.UNKNOWN

    city, country = "", ""
    try:
        import geoip2.database
        import os
        geoip_path = os.environ.get("GEOIP_PATH", "/app/geoip/GeoLite2-City.mmdb")
        if os.path.exists(geoip_path):
            with geoip2.database.Reader(geoip_path) as reader:
                geo = reader.city(ip)
                city = geo.city.name or ""
                country = geo.country.name or ""
    except Exception:
        pass

    session_key = refresh_token["jti"]

    return UserSession.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip,
        city=city,
        country=country,
        device=device_str[:200],
        device_type=device_type,
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        AuditMixin.log_action(
            user=user,
            action=AuditLog.ActionChoices.CREATE,
            entity_type="User",
            entity_id=user.pk,
            request=request,
        )

        return Response(
            {"detail": "Inscription réussie. Votre adhésion est en attente de validation."},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        _create_session(user, request, refresh)

        AuditMixin.log_action(
            user=user,
            action=AuditLog.ActionChoices.LOGIN,
            entity_type="User",
            entity_id=user.pk,
            request=request,
        )

        response = Response({"detail": "Connexion réussie."}, status=status.HTTP_200_OK)
        set_jwt_cookies(response, access, refresh)
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                jti = token.payload.get("jti", "")
                token.blacklist()
            except (TokenError, InvalidToken):
                jti = ""

            if jti:
                UserSession.objects.filter(
                    user=request.user,
                    session_key=jti,
                    is_active=True,
                ).update(is_active=False, ended_at=timezone.now())

        AuditMixin.log_action(
            user=request.user,
            action=AuditLog.ActionChoices.LOGOUT,
            entity_type="User",
            entity_id=request.user.pk,
            request=request,
        )

        response = Response({"detail": "Déconnexion réussie."}, status=status.HTTP_200_OK)
        delete_jwt_cookies(response)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(request.user).data)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])

        OutstandingToken.objects.filter(user=request.user).delete()

        response = Response({"detail": "Mot de passe modifié. Veuillez vous reconnecter."})
        delete_jwt_cookies(response)
        return response


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_data = serializer.get_reset_data()

        if reset_data:
            # TODO: envoyer l'email via Celery task
            # Pour le moment, log le lien de reset pour le développement
            pass

        return Response(
            {"detail": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."}
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        OutstandingToken.objects.filter(user=user).delete()

        return Response({"detail": "Mot de passe réinitialisé avec succès."})


class CookieTokenRefreshView(APIView):
    """Lit le refresh token depuis le cookie, retourne un nouveau access + refresh."""

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_cookie = request.COOKIES.get(
            settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )

        if not refresh_cookie:
            return Response(
                {"detail": "Aucun refresh token fourni."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            old_token = RefreshToken(refresh_cookie)
            new_access = old_token.access_token

            # ROTATE_REFRESH_TOKENS=True → on génère un nouveau refresh
            from apps.accounts.models import User
            user = User.objects.get(pk=old_token.payload["user_id"])
            new_refresh = RefreshToken.for_user(user)

            # Blackliste l'ancien
            old_token.blacklist()

            old_jti = old_token.payload.get("jti", "")
            new_jti = new_refresh.payload.get("jti", "")
            if old_jti and new_jti:
                UserSession.objects.filter(
                    user=user,
                    session_key=old_jti,
                    is_active=True,
                ).update(session_key=new_jti)

        except (TokenError, InvalidToken, User.DoesNotExist):
            response = Response(
                {"detail": "Refresh token invalide ou expiré."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            delete_jwt_cookies(response)
            return response

        response = Response({"detail": "Token rafraîchi."})
        set_jwt_cookies(response, new_access, new_refresh)
        return response
