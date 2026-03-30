from django.conf import settings


def set_jwt_cookies(response, access_token, refresh_token=None):
    """Place les tokens JWT dans des cookies httpOnly sur la response."""
    jwt_settings = settings.SIMPLE_JWT

    response.set_cookie(
        key=jwt_settings["AUTH_COOKIE"],
        value=str(access_token),
        httponly=jwt_settings["AUTH_COOKIE_HTTP_ONLY"],
        secure=jwt_settings["AUTH_COOKIE_SECURE"],
        samesite=jwt_settings["AUTH_COOKIE_SAMESITE"],
        path=jwt_settings["AUTH_COOKIE_PATH"],
        max_age=int(jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds()),
    )

    if refresh_token:
        response.set_cookie(
            key=jwt_settings["AUTH_COOKIE_REFRESH"],
            value=str(refresh_token),
            httponly=jwt_settings["AUTH_COOKIE_HTTP_ONLY"],
            secure=jwt_settings["AUTH_COOKIE_SECURE"],
            samesite=jwt_settings["AUTH_COOKIE_SAMESITE"],
            path=jwt_settings.get("AUTH_COOKIE_REFRESH_PATH", "/"),
            max_age=int(jwt_settings["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        )


def delete_jwt_cookies(response):
    """Supprime les cookies JWT de la response."""
    jwt_settings = settings.SIMPLE_JWT
    response.delete_cookie(
        jwt_settings["AUTH_COOKIE"],
        path=jwt_settings["AUTH_COOKIE_PATH"],
    )
    response.delete_cookie(
        jwt_settings["AUTH_COOKIE_REFRESH"],
        path=jwt_settings.get("AUTH_COOKIE_REFRESH_PATH", "/"),
    )


def get_client_ip(request):
    """Extrait l'IP client en tenant compte des proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
