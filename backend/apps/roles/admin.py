from django.contrib import admin

from apps.roles.models import PartyRole, UserPartyRole


@admin.register(PartyRole)
class PartyRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "is_active", "created_at")
    list_filter = ("level", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserPartyRole)
class UserPartyRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "zone", "is_active", "created_at")
    list_filter = ("is_active", "role__level")
    search_fields = ("user__email", "role__name")
    raw_id_fields = ("user", "assigned_by")
