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
