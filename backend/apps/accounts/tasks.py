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

PRESIDENT_EMAIL = "dabenogbo45@gmail.com"
FALLBACK_PARTY_EMAIL = "info@fpp-ci.online"


def _get_party_recipients():
    """Retourne la liste dédupliquée des emails du parti (SiteSettings + président)."""
    from apps.site_settings.models import SiteSettings

    recipients = set()
    try:
        site = SiteSettings.load()
        if site.contact_email:
            recipients.add(site.contact_email)
    except Exception:
        pass

    recipients.add(PRESIDENT_EMAIL)

    if not recipients:
        recipients.add(FALLBACK_PARTY_EMAIL)

    return list(recipients)


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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_contact_acknowledgment(self, contact_id):
    """Envoie un accusé de réception au visiteur qui a soumis le formulaire de contact."""
    from apps.contact.models import ContactMessage

    try:
        msg = ContactMessage.objects.get(pk=contact_id)
    except ContactMessage.DoesNotExist:
        logger.warning("send_contact_acknowledgment: message %s introuvable", contact_id)
        return

    if not msg.email:
        return

    message_excerpt = msg.message[:300]
    if len(msg.message) > 300:
        message_excerpt += "…"

    try:
        _send_html_email(
            subject="FPP — Merci pour votre message !",
            template_name="emails/contact_acknowledgment.html",
            context={
                "name": msg.name,
                "subject": msg.subject,
                "message_excerpt": message_excerpt,
            },
            recipient_list=[msg.email],
            reply_to=[getattr(settings, "CONTACT_DEST_EMAIL", settings.DEFAULT_FROM_EMAIL)],
        )
        logger.info("Accusé de réception contact envoyé à %s", msg.email)
    except Exception as exc:
        logger.error("Échec envoi accusé de réception contact à %s: %s", msg.email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_party_new_signup(self, user_id):
    """Notifie le parti qu'un nouveau sympathisant s'est inscrit (avant vérification email)."""
    from apps.accounts.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("notify_party_new_signup: user %s introuvable", user_id)
        return

    recipients = _get_party_recipients()
    frontend_url = getattr(settings, "FRONTEND_URL", "https://fpp-ci.online")

    try:
        _send_html_email(
            subject=f"FPP — Nouvelle inscription : {user.full_name}",
            template_name="emails/admin_new_signup.html",
            context={
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone or "Non renseigné",
                "sex": user.get_sex_display() if user.sex else "Non renseigné",
                "date_of_birth": user.date_of_birth.strftime("%d/%m/%Y") if user.date_of_birth else "Non renseignée",
                "registration_date": user.created_at.strftime("%d/%m/%Y à %H:%M"),
                "email_verified": user.email_verified,
                "admin_link": f"{frontend_url}/admin/members",
            },
            recipient_list=recipients,
            reply_to=[user.email],
        )
        logger.info("Notification nouvelle inscription envoyée pour %s", user.email)
    except Exception as exc:
        logger.error("Échec envoi notification inscription %s: %s", user.email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_party_email_verified(self, user_id):
    """Notifie le parti qu'un sympathisant a confirmé son adresse email."""
    from apps.accounts.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("notify_party_email_verified: user %s introuvable", user_id)
        return

    recipients = _get_party_recipients()
    frontend_url = getattr(settings, "FRONTEND_URL", "https://fpp-ci.online")

    try:
        _send_html_email(
            subject=f"FPP — Email confirmé : {user.full_name}",
            template_name="emails/admin_email_verified.html",
            context={
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone or "Non renseigné",
                "sex": user.get_sex_display() if user.sex else "Non renseigné",
                "date_of_birth": user.date_of_birth.strftime("%d/%m/%Y") if user.date_of_birth else "Non renseignée",
                "registration_date": user.created_at.strftime("%d/%m/%Y à %H:%M"),
                "admin_link": f"{frontend_url}/admin/members",
            },
            recipient_list=recipients,
            reply_to=[user.email],
        )
        logger.info("Notification email vérifié envoyée pour %s", user.email)
    except Exception as exc:
        logger.error("Échec envoi notification email vérifié %s: %s", user.email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_party_membership_request(self, user_id):
    """Notifie le parti qu'un sympathisant a soumis une demande d'adhésion (Phase 2)."""
    from apps.accounts.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("notify_party_membership_request: user %s introuvable", user_id)
        return

    profile = getattr(user, "member_profile", None)
    if not profile:
        return

    recipients = _get_party_recipients()
    frontend_url = getattr(settings, "FRONTEND_URL", "https://fpp-ci.online")
    backend_url = getattr(settings, "BACKEND_URL", "https://api.fpp-ci.online")

    photo_url = f"{backend_url}{profile.photo.url}" if profile.photo else ""
    id_scan_url = f"{backend_url}{profile.id_document_scan.url}" if profile.id_document_scan else ""

    try:
        _send_html_email(
            subject=f"FPP — Demande d'adhésion : {user.full_name}",
            template_name="emails/admin_membership_request.html",
            context={
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone or "Non renseigné",
                "sex": user.get_sex_display() if user.sex else "Non renseigné",
                "date_of_birth": user.date_of_birth.strftime("%d/%m/%Y") if user.date_of_birth else "Non renseignée",
                "registration_date": user.created_at.strftime("%d/%m/%Y à %H:%M"),
                "id_document_type": profile.get_id_document_type_display(),
                "id_document_number": profile.id_document_number,
                "photo_url": photo_url,
                "id_scan_url": id_scan_url,
                "city": profile.city,
                "commune": profile.commune,
                "region": profile.region or "Non renseignée",
                "neighborhood": profile.neighborhood or "Non renseigné",
                "address": profile.address or "Non renseignée",
                "profession": profile.profession or "Non renseignée",
                "motivation": profile.motivation or "Non renseignée",
                "registration_source": profile.get_registration_source_display(),
                "admin_link": f"{frontend_url}/admin/members",
            },
            recipient_list=recipients,
            reply_to=[user.email],
        )
        logger.info("Notification demande adhésion envoyée pour %s", user.email)
    except Exception as exc:
        logger.error("Échec envoi notification adhésion %s: %s", user.email, exc)
        raise self.retry(exc=exc)
