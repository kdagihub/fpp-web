import logging
from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

logger = logging.getLogger(__name__)


def _send_html_email(subject, template_name, context, recipient_list, reply_to=None):
    """Render an HTML email from a template and send with plain-text fallback."""
    context.setdefault("year", datetime.now().year)

    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
        reply_to=reply_to or [],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_verification(self, user_id):
    """Envoie l'email de vérification après inscription."""
    from apps.accounts.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_email_verification: user %s introuvable", user_id)
        return

    if user.email_verified:
        return

    uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
    token = default_token_generator.make_token(user)
    frontend_url = getattr(settings, "FRONTEND_URL", "https://fpp-ci.online")
    verify_link = f"{frontend_url}/verify-email?uid={uid}&token={token}"

    try:
        _send_html_email(
            subject="FPP — Vérifiez votre adresse email",
            template_name="emails/verify_email.html",
            context={
                "first_name": user.first_name,
                "verify_link": verify_link,
            },
            recipient_list=[user.email],
        )
        logger.info("Email de vérification envoyé à %s", user.email)
    except Exception as exc:
        logger.error("Échec envoi email vérification à %s: %s", user.email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id, uid, token):
    """Envoie l'email de réinitialisation de mot de passe."""
    from apps.accounts.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_password_reset_email: user %s introuvable", user_id)
        return

    frontend_url = getattr(settings, "FRONTEND_URL", "https://fpp-ci.online")
    reset_link = f"{frontend_url}/password-reset/confirm?uid={uid}&token={token}"

    try:
        _send_html_email(
            subject="FPP — Réinitialisation de votre mot de passe",
            template_name="emails/password_reset.html",
            context={
                "first_name": user.first_name,
                "reset_link": reset_link,
            },
            recipient_list=[user.email],
        )
        logger.info("Email de reset envoyé à %s", user.email)
    except Exception as exc:
        logger.error("Échec envoi email reset à %s: %s", user.email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """Envoie l'email de bienvenue après vérification de l'email."""
    from apps.accounts.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    frontend_url = getattr(settings, "FRONTEND_URL", "https://fpp-ci.online")
    dashboard_link = f"{frontend_url}/mon-espace"

    try:
        _send_html_email(
            subject="FPP — Bienvenue au Front Patriotique Panafricain !",
            template_name="emails/welcome.html",
            context={
                "first_name": user.first_name,
                "dashboard_link": dashboard_link,
            },
            recipient_list=[user.email],
        )
    except Exception as exc:
        logger.error("Échec envoi email bienvenue à %s: %s", user.email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_contact_message(self, contact_id):
    """Envoie un email de notification au parti quand un visiteur soumet le formulaire de contact."""
    from apps.contact.models import ContactMessage

    try:
        msg = ContactMessage.objects.get(pk=contact_id)
    except ContactMessage.DoesNotExist:
        logger.warning("notify_contact_message: message %s introuvable", contact_id)
        return

    party_email = getattr(settings, "CONTACT_DEST_EMAIL", settings.DEFAULT_FROM_EMAIL)

    try:
        _send_html_email(
            subject=f"FPP — Nouveau message de contact : {msg.subject}",
            template_name="emails/contact_notification.html",
            context={
                "name": msg.name,
                "email": msg.email,
                "phone": msg.phone or "",
                "subject": msg.subject,
                "message": msg.message,
                "date": msg.created_at.strftime("%d/%m/%Y à %H:%M"),
            },
            recipient_list=[party_email],
            reply_to=[msg.email],
        )
        logger.info("Email de notification contact envoyé pour message %s", contact_id)
    except Exception as exc:
        logger.error("Échec envoi notification contact %s: %s", contact_id, exc)
        raise self.retry(exc=exc)


@shared_task
def notify_admins_new_registration(user_id):
    """Notifie les admins d'une nouvelle demande d'adhésion."""
    from apps.accounts.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    admin_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .values_list("email", flat=True)
    )
    if not admin_emails:
        return

    profile = getattr(user, "member_profile", None)
    doc_info = ""
    if profile:
        doc_info = f"{profile.get_id_document_type_display()} — {profile.id_document_number}"

    frontend_url = getattr(settings, "FRONTEND_URL", "https://fpp-ci.online")

    try:
        _send_html_email(
            subject=f"FPP — Nouvelle demande d'adhésion : {user.full_name}",
            template_name="emails/admin_new_registration.html",
            context={
                "full_name": user.full_name,
                "email": user.email,
                "doc_info": doc_info,
                "registration_date": user.created_at.strftime("%d/%m/%Y %H:%M"),
                "admin_link": f"{frontend_url}/admin/members",
            },
            recipient_list=admin_emails,
        )
    except Exception:
        pass
