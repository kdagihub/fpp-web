from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from apps.accounts.models import User
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

REFRESH_GRACE_SECONDS = 30


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

        from apps.accounts.tasks import send_email_verification
        send_email_verification.delay(str(user.pk))

        return Response(
            {
                "detail": "Compte créé. Un email de vérification a été envoyé à votre adresse. "
                "Veuillez vérifier votre boîte de réception pour activer votre compte."
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        with transaction.atomic():
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

        with transaction.atomic():
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
        user = (
            User.objects
            .select_related("member_profile")
            .prefetch_related("party_roles__role", "party_roles__zone")
            .get(pk=request.user.pk)
        )
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = (
            User.objects
            .select_related("member_profile")
            .prefetch_related("party_roles__role", "party_roles__zone")
            .get(pk=request.user.pk)
        )
        return Response(UserProfileSerializer(user).data)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
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
            from apps.accounts.tasks import send_password_reset_email
            send_password_reset_email.delay(
                str(reset_data["user"].pk),
                reset_data["uid"],
                reset_data["token"],
            )

        return Response(
            {"detail": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."}
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        with transaction.atomic():
            user.set_password(serializer.validated_data["new_password"])
            user.save(update_fields=["password"])
            OutstandingToken.objects.filter(user=user).delete()

        return Response({"detail": "Mot de passe réinitialisé avec succès."})


class CookieTokenRefreshView(APIView):
    """
    Lit le refresh token depuis le cookie, retourne un nouveau access + refresh.
    Grace period de 30s : si le même refresh arrive 2 fois (réseau instable),
    on retourne les tokens cachés au lieu de rejeter.
    """

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

        cache_key = f"token_refresh_grace:{hash(refresh_cookie)}"
        cached = cache.get(cache_key)
        if cached:
            response = Response({"detail": "Token rafraîchi."})
            set_jwt_cookies(response, cached["access"], cached["refresh"])
            return response

        try:
            old_token = RefreshToken(refresh_cookie)

            user = User.objects.get(pk=old_token.payload["user_id"])

            with transaction.atomic():
                new_refresh = RefreshToken.for_user(user)
                new_access = new_refresh.access_token
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

        cache.set(cache_key, {
            "access": str(new_access),
            "refresh": str(new_refresh),
        }, REFRESH_GRACE_SECONDS)

        response = Response({"detail": "Token rafraîchi."})
        set_jwt_cookies(response, new_access, new_refresh)
        return response


class VerifyEmailView(APIView):
    """Vérifie l'email de l'utilisateur via uid + token (lien envoyé par mail)."""

    permission_classes = [AllowAny]

    def post(self, request):
        uid_encoded = request.data.get("uid")
        token = request.data.get("token")

        if not uid_encoded or not token:
            return Response(
                {"detail": "uid et token sont requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = urlsafe_base64_decode(uid_encoded).decode()
            user = User.objects.get(pk=uid)
        except (ValueError, TypeError, User.DoesNotExist):
            return Response(
                {"detail": "Lien de vérification invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.email_verified:
            return Response({"detail": "Cet email est déjà vérifié."})

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Le lien de vérification a expiré ou est invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user.email_verified = True
            user.save(update_fields=["email_verified", "updated_at"])

        AuditMixin.log_action(
            user=user,
            action=AuditLog.ActionChoices.UPDATE,
            entity_type="User",
            entity_id=user.pk,
            changes={"email_verified": True},
            request=request,
        )

        from apps.accounts.tasks import send_welcome_email
        send_welcome_email.delay(str(user.pk))

        return Response({"detail": "Email vérifié avec succès. Vous pouvez maintenant vous connecter."})


class ResendVerificationView(APIView):
    """Renvoie l'email de vérification. Throttled pour éviter les abus."""

    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        email = request.data.get("email", "").lower().strip()
        if not email:
            return Response(
                {"detail": "L'email est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            pass
        else:
            if not user.email_verified:
                from apps.accounts.tasks import send_email_verification
                send_email_verification.delay(str(user.pk))

        return Response(
            {"detail": "Si un compte non vérifié existe avec cet email, un nouveau lien a été envoyé."}
        )
