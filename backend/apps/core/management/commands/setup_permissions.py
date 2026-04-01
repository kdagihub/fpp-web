from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.content.models import Article, Category
from apps.contact.models import ContactMessage
from apps.core.models import AuditLog
from apps.members.models import MemberProfile
from apps.roles.models import UserPartyRole
from apps.site_settings.models import SiteSettings

CUSTOM_PERMISSIONS = [
    ("members", "memberprofile", "can_view_members", "Voir les membres"),
    ("members", "memberprofile", "can_manage_members", "Gérer les membres"),
    ("members", "memberprofile", "can_validate_membership", "Valider une adhésion"),
    ("members", "memberprofile", "can_export_members", "Exporter les membres"),
    ("content", "article", "can_create_article", "Créer un article"),
    ("content", "article", "can_edit_article", "Modifier un article"),
    ("content", "article", "can_delete_article", "Supprimer un article"),
    ("content", "category", "can_manage_categories", "Gérer les catégories"),
    ("contact", "contactmessage", "can_manage_contacts", "Gérer les messages"),
    ("contact", "contactmessage", "can_export_contacts", "Exporter les messages"),
    ("core", "auditlog", "can_view_dashboard", "Voir le dashboard"),
    ("core", "auditlog", "can_view_audit_log", "Voir le journal d'audit"),
    ("site_settings", "sitesettings", "can_manage_settings", "Gérer les paramètres du site"),
    ("roles", "userpartyrole", "can_assign_roles", "Assigner des rôles"),
]

GROUPS = {
    "Éditeur": [
        "can_create_article",
        "can_edit_article",
        "can_manage_categories",
    ],
    "Gestionnaire": [
        "can_create_article",
        "can_edit_article",
        "can_manage_categories",
        "can_manage_members",
        "can_validate_membership",
        "can_export_members",
        "can_manage_contacts",
        "can_export_contacts",
        "can_view_dashboard",
    ],
    "Super Admin": [
        "can_create_article",
        "can_edit_article",
        "can_delete_article",
        "can_manage_categories",
        "can_manage_members",
        "can_validate_membership",
        "can_export_members",
        "can_view_members",
        "can_manage_contacts",
        "can_export_contacts",
        "can_view_dashboard",
        "can_manage_settings",
        "can_assign_roles",
        "can_view_audit_log",
    ],
}


class Command(BaseCommand):
    help = "Crée les permissions personnalisées et les groupes du SPECS."

    def handle(self, *args, **options):
        created_perms = 0
        for app_label, model_name, codename, name in CUSTOM_PERMISSIONS:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
            _, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=ct,
                defaults={"name": name},
            )
            if created:
                created_perms += 1
                self.stdout.write(f"  + Permission: {codename}")

        self.stdout.write(self.style.SUCCESS(f"{created_perms} permission(s) créée(s)."))

        created_groups = 0
        for group_name, perm_codenames in GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                created_groups += 1

            perms = Permission.objects.filter(codename__in=perm_codenames)
            group.permissions.set(perms)
            self.stdout.write(f"  {'+ Groupe' if created else '~ Groupe'}: {group_name} ({perms.count()} permissions)")

        self.stdout.write(self.style.SUCCESS(f"{created_groups} groupe(s) créé(s). Terminé."))
