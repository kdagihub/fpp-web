from django.contrib import admin

from apps.members.models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("matricule", "user", "sex", "city", "commune", "membership_status", "created_at")
    list_filter = ("membership_status", "sex", "registration_source", "region")
    search_fields = ("matricule", "user__email", "user__first_name", "user__last_name", "city", "commune")
    readonly_fields = ("matricule", "created_at", "updated_at")
    raw_id_fields = ("user",)
