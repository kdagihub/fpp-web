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
from apps.api.views.bureau import AdminBureauDetailView, AdminBureauListCreateView, PublicBureauListView
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
    AdminDocumentDetailView,
    AdminDocumentListCreateView,
    AdminDocumentPreviewView,
    AdminEventDetailView,
    AdminEventListCreateView,
    AdminMediaContentDetailView,
    AdminMediaContentListCreateView,
    AdminProgramItemDetailView,
    AdminProgramItemListCreateView,
    AdminProgramSectionDetailView,
    AdminProgramSectionListCreateView,
    PublicArticleDetailView,
    PublicArticleListView,
    PublicCategoryListView,
    PublicDocumentDownloadView,
    PublicDocumentListView,
    PublicDocumentPreviewView,
    PublicEventDetailView,
    PublicEventListView,
    PublicMediaContentListView,
    PublicProgramSectionDetailView,
    PublicProgramSectionListView,
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
from apps.api.views.pdf import (
    AdminMemberPdfView,
    MyProfilePdfView,
    PublicMembershipFormPdfView,
    PublicRegistrationFormPdfView,
)
from apps.api.views.share import ShareArticleView, ShareEventView, ShareProgrammeView
from apps.api.views.site_settings import AdminSiteSettingsView, PublicSiteSettingsView
from apps.emergency.views import EmergencyPurgeView

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
    path("me/pdf/", MyProfilePdfView.as_view(), name="my-profile-pdf"),
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
    path("media/", PublicMediaContentListView.as_view(), name="public-media"),
    path("programme/", PublicProgramSectionListView.as_view(), name="public-programme"),
    path("programme/<slug:slug>/", PublicProgramSectionDetailView.as_view(), name="public-programme-detail"),
    path("events/", PublicEventListView.as_view(), name="public-events"),
    path("events/<slug:slug>/", PublicEventDetailView.as_view(), name="public-event-detail"),
    path("stats/", PublicStatsView.as_view(), name="public-stats"),
    path("registration-form/pdf/", PublicRegistrationFormPdfView.as_view(), name="public-registration-pdf"),
    path("membership-form/pdf/", PublicMembershipFormPdfView.as_view(), name="public-membership-pdf"),
    path("bureau/", PublicBureauListView.as_view(), name="public-bureau"),
    path("documents/", PublicDocumentListView.as_view(), name="public-documents"),
    path("documents/<uuid:pk>/download/", PublicDocumentDownloadView.as_view(), name="public-document-download"),
    path("documents/<uuid:pk>/preview/", PublicDocumentPreviewView.as_view(), name="public-document-preview"),
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
    path("members/<uuid:pk>/pdf/", AdminMemberPdfView.as_view(), name="admin-member-pdf"),

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

    # Médias
    path("media/", AdminMediaContentListCreateView.as_view(), name="admin-media"),
    path("media/<uuid:pk>/", AdminMediaContentDetailView.as_view(), name="admin-media-detail"),

    # Programme
    path("programme/sections/", AdminProgramSectionListCreateView.as_view(), name="admin-programme-sections"),
    path("programme/sections/<uuid:pk>/", AdminProgramSectionDetailView.as_view(), name="admin-programme-section-detail"),
    path("programme/items/", AdminProgramItemListCreateView.as_view(), name="admin-programme-items"),
    path("programme/items/<uuid:pk>/", AdminProgramItemDetailView.as_view(), name="admin-programme-item-detail"),

    # Événements / Agenda
    path("events/", AdminEventListCreateView.as_view(), name="admin-events"),
    path("events/<uuid:pk>/", AdminEventDetailView.as_view(), name="admin-event-detail"),

    # Contacts
    path("contacts/", AdminContactListView.as_view(), name="admin-contacts"),
    path("contacts/export/", AdminContactExportView.as_view(), name="admin-contacts-export"),
    path("contacts/<uuid:pk>/", AdminContactDetailView.as_view(), name="admin-contact-detail"),

    # Settings
    path("settings/", AdminSiteSettingsView.as_view(), name="admin-settings"),

    # Bureau National
    path("bureau/", AdminBureauListCreateView.as_view(), name="admin-bureau-list"),
    path("bureau/<uuid:pk>/", AdminBureauDetailView.as_view(), name="admin-bureau-detail"),

    # Documents
    path("documents/", AdminDocumentListCreateView.as_view(), name="admin-documents"),
    path("documents/<uuid:pk>/", AdminDocumentDetailView.as_view(), name="admin-document-detail"),
    path("documents/<uuid:pk>/preview/", AdminDocumentPreviewView.as_view(), name="admin-document-preview"),

    # Audit log
    path("audit-log/", AdminAuditLogView.as_view(), name="admin-audit-log"),
]

# ---------------------------------------------------------------------------
# Share (OG meta pour crawlers sociaux)
# ---------------------------------------------------------------------------
share_urlpatterns = [
    path("article/<slug:slug>/", ShareArticleView.as_view(), name="share-article"),
    path("event/<slug:slug>/", ShareEventView.as_view(), name="share-event"),
    path("programme/<slug:slug>/", ShareProgrammeView.as_view(), name="share-programme"),
]

# ---------------------------------------------------------------------------
# Emergency
# ---------------------------------------------------------------------------
emergency_urlpatterns = [
    path("purge/", EmergencyPurgeView.as_view(), name="emergency-purge"),
]

# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------
urlpatterns = [
    path("auth/", include((auth_urlpatterns, "auth"))),
    path("membership/", include((membership_urlpatterns, "membership"))),
    path("public/", include((public_urlpatterns, "public"))),
    path("admin/", include((admin_urlpatterns, "admin-api"))),
    path("share/", include((share_urlpatterns, "share"))),
    path("emergency/", include((emergency_urlpatterns, "emergency"))),
]
