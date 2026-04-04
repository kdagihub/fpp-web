from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import ConsentLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "email_verified", "is_staff", "is_emergency_user", "is_active", "cgu_accepted_at", "created_at")
    list_filter = ("is_staff", "is_active", "is_emergency_user", "email_verified", "created_at")
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations personnelles", {"fields": ("first_name", "last_name", "sex", "phone", "date_of_birth", "avatar")}),
        ("Vérification", {"fields": ("email_verified",)}),
        ("Consentement (Loi 2013-450)", {"fields": ("cgu_accepted_at", "privacy_accepted_at", "cgu_ip_address")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_emergency_user", "groups", "user_permissions")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "cgu_accepted_at", "privacy_accepted_at", "cgu_ip_address")

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )


@admin.register(ConsentLog)
class ConsentLogAdmin(admin.ModelAdmin):
    list_display = ("user", "consent_type", "version", "ip_address", "accepted_at")
    list_filter = ("consent_type", "version", "accepted_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "ip_address")
    readonly_fields = ("user", "consent_type", "version", "ip_address", "user_agent", "accepted_at")
    ordering = ("-accepted_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
