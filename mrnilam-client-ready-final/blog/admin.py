from django.contrib import admin
from django.utils.html import format_html

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title_en", "article_type", "status", "translation_status", "is_featured", "published_date", "expires_at", "updated_at")
    list_filter = ("status", "article_type", "is_featured", "alert_severity", "language", "published_date", "expires_at")
    search_fields = ("title_en", "title_ne", "summary_en", "summary_ne", "content_en", "content_ne")
    prepopulated_fields = {"slug": ("title_en",)}
    date_hierarchy = "published_date"
    readonly_fields = ("updated_at", "translation_status", "meta_title", "meta_description")
    fieldsets = (
        ("Publishing", {"fields": ("article_type", "status", "published_date", "expires_at", "is_featured", "language", "author_name", "translation_status")}),
        ("Titles and summaries", {"fields": ("title_ne", "title_en", "slug", "summary_ne", "summary_en")}),
        ("Content", {"fields": ("content_ne", "content_en")}),
        ("Image", {"fields": ("featured_image_file", "featured_image_url", "image_alt_ne", "image_alt_en")}),
        ("Alert", {"fields": ("is_alert", "alert_severity")}),
        ("SEO — Nepali", {"fields": ("meta_title_ne", "meta_description_ne"), "classes": ("collapse",)}),
        ("SEO — English", {"fields": ("meta_title_en", "meta_description_en"), "classes": ("collapse",)}),
        ("Legacy SEO metadata", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Audit", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )

    @admin.display(description="Bilingual completeness")
    def translation_status(self, obj):
        complete = all([obj.title_ne.strip(), obj.title_en.strip(), obj.content_ne.strip(), obj.content_en.strip()])
        if complete:
            return format_html('<span style="color:#166534;font-weight:700">Complete</span>')
        return format_html('<span style="color:#991b1b;font-weight:700">Needs translation</span>')

    def has_delete_permission(self, request, obj=None):
        return False
