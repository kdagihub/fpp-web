import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

logger = logging.getLogger(__name__)


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
        send_mail(
            subject="FPP — Vérifiez votre adresse email",
            message=(
                f"Bonjour {user.first_name},\n\n"
                f"Bienvenue au Front Patriotique Panafricain !\n\n"
                f"Pour activer votre compte, veuillez vérifier votre email "
                f"en cliquant sur le lien suivant :\n"
                f"{verify_link}\n\n"
                f"Ce lien expire dans 24 heures.\n\n"
                f"Si vous n'avez pas créé ce compte, ignorez cet email.\n\n"
                f"— L'équipe FPP"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
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
    reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"

    try:
        send_mail(
            subject="FPP — Réinitialisation de votre mot de passe",
            message=(
                f"Bonjour {user.first_name},\n\n"
                f"Cliquez sur ce lien pour réinitialiser votre mot de passe :\n"
                f"{reset_link}\n\n"
                f"Ce lien expire dans 24 heures.\n\n"
                f"Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.\n\n"
                f"— L'équipe FPP"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
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

    try:
        send_mail(
            subject="FPP — Bienvenue au Front Patriotique Panafricain !",
            message=(
                f"Bonjour {user.first_name},\n\n"
                f"Votre email a été vérifié avec succès.\n"
                f"Votre compte sympathisant FPP est désormais actif.\n\n"
                f"Vous pouvez dès maintenant accéder aux actualités publiques "
                f"et aux newsletters depuis votre tableau de bord.\n\n"
                f"Pour devenir membre à part entière, soumettez une demande "
                f"d'adhésion depuis votre profil.\n\n"
                f"— L'équipe FPP"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error("Échec envoi email bienvenue à %s: %s", user.email, exc)
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
        doc_info = f"Pièce d'identité : {profile.get_id_document_type_display()} — {profile.id_document_number}\n"

    try:
        send_mail(
            subject=f"FPP — Nouvelle demande d'adhésion : {user.full_name}",
            message=(
                f"Nouvelle demande d'adhésion reçue :\n\n"
                f"Nom : {user.full_name}\n"
                f"Email : {user.email}\n"
                f"{doc_info}"
                f"Date : {user.created_at.strftime('%d/%m/%Y %H:%M')}\n\n"
                f"Connectez-vous au backoffice pour examiner cette demande."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=True,
        )
    except Exception:
        pass
