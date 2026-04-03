from django.contrib import admin

from apps.content.models import Article, Category, Event, MediaContent, ProgramItem, ProgramSection


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status", "is_featured", "published_at")
    list_filter = ("status", "is_featured", "category")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)


@admin.register(MediaContent)
class MediaContentAdmin(admin.ModelAdmin):
    list_display = ("title", "platform", "embed_type", "category", "is_featured", "is_active", "published_at")
    list_filter = ("platform", "embed_type", "is_featured", "is_active", "category")
    search_fields = ("title", "description")
    list_editable = ("is_featured", "is_active")


class ProgramItemInline(admin.TabularInline):
    model = ProgramItem
    extra = 1
    fields = ("title", "description", "order", "is_active")


@admin.register(ProgramSection)
class ProgramSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProgramItemInline]


@admin.register(ProgramItem)
class ProgramItemAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "order", "is_active")
    list_filter = ("section", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title", "description")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "status", "start_date", "city", "is_featured", "is_active")
    list_filter = ("status", "event_type", "is_featured", "is_active", "city")
    search_fields = ("title", "description", "location", "city")
    list_editable = ("status", "is_featured", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "start_date"
