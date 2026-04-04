from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Accès réservé aux administrateurs (is_staff)."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """L'utilisateur peut accéder à ses propres ressources, ou être admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return hasattr(obj, "user") and obj.user == request.user


class IsMember(BasePermission):
    """Accès réservé aux membres validés (MemberProfile.membership_status = validated)."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        profile = getattr(request.user, "member_profile", None)
        return profile is not None and profile.membership_status == "validated"


class HasPermission(BasePermission):
    """
    Permission générique basée sur un code permission Django.
    Usage dans la vue : permission_required = "members.can_view_members"
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        perm = getattr(view, "permission_required", None)
        if perm is None:
            return True
        return request.user.has_perm(perm)


def _is_staff(user):
    return user.is_authenticated and user.is_staff


class CanViewMembers(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("members.can_view_members")


class CanManageMembers(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("members.can_manage_members")


class CanValidateMembership(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("members.can_validate_membership")


class CanExportMembers(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("members.can_export_members")


class CanCreateArticle(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("content.can_create_article")


class CanEditArticle(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("content.can_edit_article")


class CanDeleteArticle(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("content.can_delete_article")


class CanManageCategories(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("content.can_manage_categories")


class CanManageContacts(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("contact.can_manage_contacts")


class CanExportContacts(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("contact.can_export_contacts")


class CanViewDashboard(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("core.can_view_dashboard")


class CanManageSettings(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("site_settings.can_manage_settings")


class CanAssignRoles(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("roles.can_assign_roles")


class CanManagePermissions(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("accounts.can_manage_permissions")


class CanViewAuditLog(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("core.can_view_audit_log")


class CanManageMedia(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("content.can_manage_media")


class CanManageProgram(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("content.can_manage_program")


class CanManageEvents(BasePermission):
    def has_permission(self, request, view):
        return _is_staff(request.user) or request.user.has_perm("content.can_manage_events")
