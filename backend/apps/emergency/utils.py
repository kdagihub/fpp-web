import hashlib
import io
import logging
import secrets
import string
from datetime import datetime

import pyzipper
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.db import connection
from openpyxl import Workbook

from apps.accounts.models import User
from apps.members.models import MemberProfile

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "emergency:code:"

CONFIRMATION_TEXT = "URGENCE SUPPRESSION"


def verify_code(code: str) -> bool:
    """Vérifie que le hash du code fourni correspond à l'un des codes
    stockés dans Redis pour les emails d'urgence."""
    emails: list[str] = getattr(settings, "EMERGENCY_EMAILS", [])
    code_hash = hashlib.sha256(code.encode()).hexdigest()

    for email in emails:
        stored_hash = cache.get(f"{CACHE_KEY_PREFIX}{email}")
        if stored_hash and stored_hash == code_hash:
            return True
    return False


def export_users_excel() -> io.BytesIO:
    """Exporte Users + MemberProfiles dans un classeur Excel en mémoire."""
    wb = Workbook()

    # --- Onglet Users ---
    ws_users = wb.active
    ws_users.title = "Utilisateurs"
    user_fields = [
        "id", "email", "phone", "first_name", "last_name", "sex",
        "date_of_birth", "email_verified", "is_active", "is_staff",
        "created_at", "updated_at",
    ]
    ws_users.append(user_fields)

    for u in User.objects.all().order_by("created_at"):
        ws_users.append([
            str(u.id),
            u.email,
            u.phone or "",
            u.first_name,
            u.last_name,
            u.sex,
            str(u.date_of_birth) if u.date_of_birth else "",
            u.email_verified,
            u.is_active,
            u.is_staff,
            u.created_at.isoformat() if u.created_at else "",
            u.updated_at.isoformat() if u.updated_at else "",
        ])

    # --- Onglet Membres ---
    ws_members = wb.create_sheet("Profils membres")
    member_fields = [
        "user_email", "user_nom_complet", "matricule",
        "id_document_type", "id_document_number",
        "city", "commune", "region", "neighborhood",
        "profession", "motivation",
        "membership_status", "membership_date",
        "registration_source", "created_at",
    ]
    ws_members.append(member_fields)

    for m in MemberProfile.objects.select_related("user").order_by("created_at"):
        ws_members.append([
            m.user.email,
            m.user.full_name,
            m.matricule or "",
            m.id_document_type,
            m.id_document_number,
            m.city,
            m.commune,
            m.region,
            m.neighborhood,
            m.profession,
            m.motivation,
            m.membership_status,
            m.membership_date.isoformat() if m.membership_date else "",
            m.registration_source,
            m.created_at.isoformat() if m.created_at else "",
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def export_dumpdata() -> bytes:
    """Exécute dumpdata pour sauvegarder les données sensibles en JSON."""
    buf = io.StringIO()
    call_command(
        "dumpdata",
        "accounts.User",
        "members.MemberProfile",
        format="json",
        indent=2,
        stdout=buf,
    )
    return buf.getvalue().encode("utf-8")


def create_encrypted_zip(code: str, excel_bytes: io.BytesIO, json_bytes: bytes) -> io.BytesIO:
    """Crée un fichier ZIP chiffré AES-256 contenant l'export Excel et le dump JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_buf = io.BytesIO()

    with pyzipper.AESZipFile(
        zip_buf, "w",
        compression=pyzipper.ZIP_DEFLATED,
        encryption=pyzipper.WZ_AES,
    ) as zf:
        zf.setpassword(code.encode())
        zf.writestr(f"fpp_users_{timestamp}.xlsx", excel_bytes.read())
        zf.writestr(f"fpp_dump_{timestamp}.json", json_bytes)

    zip_buf.seek(0)
    return zip_buf


def send_emergency_emails(zip_buf: io.BytesIO) -> int:
    """Envoie le ZIP chiffré à tous les emails d'urgence. Retourne le nombre
    d'emails envoyés avec succès."""
    emails: list[str] = getattr(settings, "EMERGENCY_EMAILS", [])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sent = 0

    for email in emails:
        try:
            msg = EmailMessage(
                subject="[FPP] URGENCE — Sauvegarde des données",
                body=(
                    "La procédure d'urgence a été déclenchée.\n\n"
                    "Le fichier joint contient l'export complet des données "
                    "sensibles du parti (utilisateurs et profils membres).\n\n"
                    "Le ZIP est chiffré avec votre code d'urgence personnel.\n\n"
                    "— Système de sécurité FPP"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            zip_buf.seek(0)
            msg.attach(
                f"fpp_emergency_{timestamp}.zip",
                zip_buf.read(),
                "application/zip",
            )
            msg.send(fail_silently=False)
            sent += 1
        except Exception:
            logger.exception("Échec d'envoi du ZIP d'urgence à %s", email)

    return sent


def purge_sensitive_data():
    """Supprime toutes les données sensibles (utilisateurs, profils membres,
    sessions, tokens blacklistés)."""
    tables_to_truncate = [
        "members_memberprofile",
        "user_sessions_usersession",
        "token_blacklist_blacklistedtoken",
        "token_blacklist_outstandingtoken",
        "django_session",
        "accounts_user_groups",
        "accounts_user_user_permissions",
        "accounts_user",
    ]

    with connection.cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
        for table in tables_to_truncate:
            try:
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
                logger.info("Table %s vidée.", table)
            except Exception:
                logger.exception("Échec TRUNCATE sur %s", table)


def create_emergency_superuser() -> dict:
    """Crée un superuser d'urgence avec un mot de passe aléatoire et envoie
    les identifiants aux emails d'urgence."""
    password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    email = "urgence@fpp-ci.online"

    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name="Admin",
        last_name="Urgence",
    )
    user.email_verified = True
    user.save(update_fields=["email_verified"])

    emails: list[str] = getattr(settings, "EMERGENCY_EMAILS", [])
    for dest in emails:
        try:
            EmailMessage(
                subject="[FPP] Nouveau compte superuser d'urgence",
                body=(
                    "La procédure de purge a été exécutée.\n\n"
                    "Un nouveau compte superuser a été créé :\n\n"
                    f"  Email : {email}\n"
                    f"  Mot de passe : {password}\n\n"
                    "Changez ce mot de passe immédiatement après connexion.\n\n"
                    "— Système de sécurité FPP"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[dest],
            ).send(fail_silently=False)
        except Exception:
            logger.exception("Échec d'envoi des identifiants d'urgence à %s", dest)

    return {"email": email, "password": password}
