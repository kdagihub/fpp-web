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
from apps.api.views.audit import AdminAuditLogView
from apps.api.views.contact import (
    AdminContactDetailView,
    AdminContactExportView,
    AdminContactListView,
    PublicContactView,
)
from apps.api.views.content import (
    AdminArticleCreateView,
    AdminArticleDetailView,
    AdminArticleListView,
    AdminCategoryDetailView,
    AdminCategoryListCreateView,
    PublicArticleDetailView,
    PublicArticleListView,
    PublicCategoryListView,
    PublicStatsView,
)
from apps.api.views.dashboard import AdminDashboardView
from apps.api.views.members import (
    AdminMemberDetailView,
    AdminMemberExportView,
    AdminMemberListView,
    AdminMemberStatusView,
    AdminMemberUpdateView,
)
from apps.api.views.membership import (
    MembershipRequestView,
    ValidateMembershipView,
    VerifyMatriculeView,
)
from apps.api.views.site_settings import AdminSiteSettingsView, PublicSiteSettingsView

app_name = "api"

# ---------------------------------------------------------------------------
# Auth (inchange)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Membership (inchange)
# ---------------------------------------------------------------------------
membership_urlpatterns = [
    path("request/", MembershipRequestView.as_view(), name="membership-request"),
    path("status/", MembershipRequestView.as_view(), name="membership-status"),
]

# ---------------------------------------------------------------------------
# Public (nouveau)
# ---------------------------------------------------------------------------
public_urlpatterns = [
    path("settings/", PublicSiteSettingsView.as_view(), name="public-settings"),
    path("articles/", PublicArticleListView.as_view(), name="public-articles"),
    path("articles/<slug:slug>/", PublicArticleDetailView.as_view(), name="public-article-detail"),
    path("categories/", PublicCategoryListView.as_view(), name="public-categories"),
    path("contact/", PublicContactView.as_view(), name="public-contact"),
    path("stats/", PublicStatsView.as_view(), name="public-stats"),
]

# ---------------------------------------------------------------------------
# Admin (etendu)
# ---------------------------------------------------------------------------
admin_urlpatterns = [
    # Dashboard
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),

    # Membres
    path("members/", AdminMemberListView.as_view(), name="admin-members"),
    path("members/export/", AdminMemberExportView.as_view(), name="admin-members-export"),
    path("members/<uuid:pk>/", AdminMemberDetailView.as_view(), name="admin-member-detail"),
    path("members/<uuid:pk>/update/", AdminMemberUpdateView.as_view(), name="admin-member-update"),
    path("members/<uuid:pk>/status/", AdminMemberStatusView.as_view(), name="admin-member-status"),

    # Adhesion (existant)
    path("membership/<uuid:pk>/validate/", ValidateMembershipView.as_view(), name="validate-membership"),
    path("verify-matricule/", VerifyMatriculeView.as_view(), name="verify-matricule"),

    # Articles
    path("articles/", AdminArticleListView.as_view(), name="admin-articles"),
    path("articles/create/", AdminArticleCreateView.as_view(), name="admin-article-create"),
    path("articles/<uuid:pk>/", AdminArticleDetailView.as_view(), name="admin-article-detail"),

    # Categories
    path("categories/", AdminCategoryListCreateView.as_view(), name="admin-categories"),
    path("categories/<uuid:pk>/", AdminCategoryDetailView.as_view(), name="admin-category-detail"),

    # Contacts
    path("contacts/", AdminContactListView.as_view(), name="admin-contacts"),
    path("contacts/export/", AdminContactExportView.as_view(), name="admin-contacts-export"),
    path("contacts/<uuid:pk>/", AdminContactDetailView.as_view(), name="admin-contact-detail"),

    # Settings
    path("settings/", AdminSiteSettingsView.as_view(), name="admin-settings"),

    # Audit log
    path("audit-log/", AdminAuditLogView.as_view(), name="admin-audit-log"),
]

# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------
urlpatterns = [
    path("auth/", include((auth_urlpatterns, "auth"))),
    path("membership/", include((membership_urlpatterns, "membership"))),
    path("public/", include((public_urlpatterns, "public"))),
    path("admin/", include((admin_urlpatterns, "admin-api"))),
]
