from django.urls import include, path

from apps.api.views.auth import (
    CookieTokenRefreshView,
    LoginView,
    LogoutView,
    MeView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    RegisterView,
)

app_name = "api"

auth_urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
]

urlpatterns = [
    path("auth/", include((auth_urlpatterns, "auth"))),
]
