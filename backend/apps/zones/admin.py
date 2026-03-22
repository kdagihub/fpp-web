from django.contrib import admin

from apps.zones.models import Zone


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "parent", "is_active")
    list_filter = ("type", "is_active")
    search_fields = ("name",)
