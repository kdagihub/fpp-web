from django.contrib import admin

from apps.core.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "entity_type", "user", "ip_address", "created_at")
    list_filter = ("action", "entity_type", "created_at")
    search_fields = ("entity_type", "user__email")
    readonly_fields = ("id", "user", "action", "entity_type", "entity_id", "changes", "ip_address", "user_agent", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
