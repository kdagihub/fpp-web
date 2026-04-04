import base64
import logging
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.api.permissions import CanViewMembers
from apps.members.models import MemberProfile

logger = logging.getLogger(__name__)

_LOGO_PATH = Path(settings.BASE_DIR) / "static" / "img" / "logo-fpp.png"


def _get_logo_data_uri() -> str:
    """Return base64 data-URI for the party logo, cached after first read."""
    if not hasattr(_get_logo_data_uri, "_cache"):
        try:
            raw = _LOGO_PATH.read_bytes()
            b64 = base64.b64encode(raw).decode()
            _get_logo_data_uri._cache = f"data:image/png;base64,{b64}"
        except FileNotFoundError:
            logger.warning("Logo FPP introuvable : %s", _LOGO_PATH)
            _get_logo_data_uri._cache = ""
    return _get_logo_data_uri._cache


def _render_pdf(template_name, context, filename):
    """Render an HTML template to PDF using WeasyPrint and return an HttpResponse."""
    import weasyprint

    context.setdefault("logo_data_uri", _get_logo_data_uri())
    html_string = render_to_string(template_name, context)
    pdf_bytes = weasyprint.HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _build_user_pdf_context(user):
    """Build the template context dict for a user's filled info sheet."""
    profile = getattr(user, "member_profile", None)

    backend_url = getattr(settings, "BACKEND_URL", "https://api.fpp-ci.online")
    photo_url = ""
    if profile and profile.photo:
        photo_url = f"{backend_url}{profile.photo.url}"

    ctx = {
        "user": user,
        "profile": profile,
        "photo_url": photo_url,
        "sex_display": user.get_sex_display() if user.sex else "Non renseigné",
        "date_of_birth": (
            user.date_of_birth.strftime("%d/%m/%Y") if user.date_of_birth else "Non renseignée"
        ),
        "registration_date": user.created_at.strftime("%d/%m/%Y à %H:%M"),
        "generated_date": datetime.now().strftime("%d/%m/%Y à %H:%M"),
    }

    if profile:
        ctx.update({
            "id_document_type": profile.get_id_document_type_display(),
            "registration_source": profile.get_registration_source_display(),
            "membership_date": (
                profile.membership_date.strftime("%d/%m/%Y")
                if profile.membership_date else "En attente"
            ),
        })

    return ctx


class PublicRegistrationFormPdfView(APIView):
    """Téléchargement public de la fiche d'inscription vide (Phase 1)."""

    permission_classes = [AllowAny]

    def get(self, request):
        return _render_pdf(
            template_name="pdf/fiche_inscription_vide.html",
            context={},
            filename="Fiche-Inscription-FPP.pdf",
        )


class PublicMembershipFormPdfView(APIView):
    """Téléchargement public du formulaire d'adhésion vide (Phase 2)."""

    permission_classes = [AllowAny]

    def get(self, request):
        return _render_pdf(
            template_name="pdf/fiche_adhesion_vide.html",
            context={},
            filename="Formulaire-Adhesion-FPP.pdf",
        )


class MyProfilePdfView(APIView):
    """Génère la fiche PDF remplie de l'utilisateur connecté."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = _build_user_pdf_context(request.user)
        safe_name = request.user.full_name.replace(" ", "-")
        return _render_pdf(
            template_name="pdf/fiche_membre.html",
            context=context,
            filename=f"Fiche-FPP-{safe_name}.pdf",
        )


class AdminMemberPdfView(APIView):
    """Admin : génère la fiche PDF d'un membre (superusers exclus)."""

    permission_classes = [IsAuthenticated, CanViewMembers]

    def get(self, request, pk):
        try:
            profile = MemberProfile.objects.select_related("user").get(pk=pk)
        except MemberProfile.DoesNotExist:
            return HttpResponse(
                b"Membre introuvable.", status=404, content_type="text/plain"
            )

        if profile.user.is_superuser:
            return HttpResponse(
                b"Acces interdit.", status=403, content_type="text/plain"
            )

        context = _build_user_pdf_context(profile.user)
        safe_name = profile.user.full_name.replace(" ", "-")
        return _render_pdf(
            template_name="pdf/fiche_membre.html",
            context=context,
            filename=f"Fiche-FPP-{safe_name}.pdf",
        )
