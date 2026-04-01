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
    ResendVerificationView,
    VerifyEmailView,
)
from apps.api.views.membership import (
    MembershipRequestView,
    ValidateMembershipView,
    VerifyMatriculeView,
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
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("resend-verification/", ResendVerificationView.as_view(), name="resend-verification"),
]

membership_urlpatterns = [
    path("request/", MembershipRequestView.as_view(), name="membership-request"),
    path("status/", MembershipRequestView.as_view(), name="membership-status"),
]

admin_urlpatterns = [
    path("membership/<uuid:pk>/validate/", ValidateMembershipView.as_view(), name="validate-membership"),
    path("verify-matricule/", VerifyMatriculeView.as_view(), name="verify-matricule"),
]

urlpatterns = [
    path("auth/", include((auth_urlpatterns, "auth"))),
    path("membership/", include((membership_urlpatterns, "membership"))),
    path("admin/", include((admin_urlpatterns, "admin-api"))),
]
