from django.contrib import admin

from apps.members.models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("matricule", "user", "id_document_type", "id_document_number", "city", "commune", "membership_status", "created_at")
    list_filter = ("membership_status", "id_document_type", "registration_source", "region")
    search_fields = ("matricule", "id_document_number", "user__email", "user__first_name", "user__last_name", "city", "commune")
    readonly_fields = ("matricule", "created_at", "updated_at")
    autocomplete_fields = ("user",)
