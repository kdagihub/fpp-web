from django.contrib import admin

from apps.user_sessions.models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "device_type", "ip_address", "city", "country", "is_active", "last_activity")
    list_filter = ("is_active", "device_type", "country")
    search_fields = ("user__email", "ip_address", "city")
    readonly_fields = ("created_at", "updated_at", "last_activity")
