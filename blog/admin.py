from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title_en", "article_type", "status", "is_featured", "published_date", "updated_at")
    list_filter = ("status", "article_type", "is_featured", "alert_severity", "language", "published_date")
    search_fields = ("title_en", "title_ne", "summary_en", "summary_ne", "content_en", "content_ne")
    prepopulated_fields = {"slug": ("title_en",)}
    date_hierarchy = "published_date"
    readonly_fields = ("updated_at",)
    fieldsets = (
        ("Publishing", {"fields": ("article_type", "status", "published_date", "is_featured", "language", "author_name")}),
        ("Titles and summaries", {"fields": ("title_ne", "title_en", "slug", "summary_ne", "summary_en")}),
        ("Content", {"fields": ("content_ne", "content_en")}),
        ("Image", {"fields": ("featured_image_file", "featured_image_url")}),
        ("Alert", {"fields": ("is_alert", "alert_severity")}),
        ("SEO", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Audit", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )
