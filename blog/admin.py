from django.contrib import admin
from django.utils.html import format_html

from migrantcenter.admin_helpers import status_badge

from .models import Article


Article._meta.verbose_name = 'News, notice or program'
Article._meta.verbose_name_plural = 'News, notices and programs'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title_en",
        "article_type",
        "status_badge",
        "translation_status",
        "is_featured",
        "published_date",
        "expires_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "article_type",
        "is_featured",
        "alert_severity",
        "language",
        "published_date",
        "expires_at",
    )
    search_fields = (
        "title_en",
        "title_ne",
        "summary_en",
        "summary_ne",
        "content_en",
        "content_ne",
    )
    prepopulated_fields = {"slug": ("title_en",)}
    date_hierarchy = "published_date"
    readonly_fields = ("updated_at", "translation_status")
    save_on_top = True
    list_per_page = 30

    fieldsets = (
        (
            'What are you publishing?',
            {
                "fields": (
                    "article_type",
                    "status",
                    "published_date",
                    "expires_at",
                    "is_featured",
                    "language",
                    "author_name",
                    "translation_status",
                ),
                "description": 'Save as a draft while editing. Publish only after both language versions and facts are checked.',
            },
        ),
        ('Title and summary', {"fields": ("title_ne", "title_en", "slug", "summary_ne", "summary_en")}),
        ('Full content', {"fields": ("content_ne", "content_en")}),
        (
            'Photo',
            {
                "fields": (
                    "featured_image_file",
                    "featured_image_url",
                    "image_alt_ne",
                    "image_alt_en",
                ),
                "description": 'Upload a photo from the device when possible. Add a short description in both languages for accessibility.',
            },
        ),
        (
            'Safety alert settings',
            {
                "fields": ("is_alert", "alert_severity"),
                "classes": ("collapse",),
            },
        ),
        (
            'Search and sharing text — Nepali',
            {"fields": ("meta_title_ne", "meta_description_ne"), "classes": ("collapse",)},
        ),
        (
            'Search and sharing text — English',
            {"fields": ("meta_title_en", "meta_description_en"), "classes": ("collapse",)},
        ),
        ('Audit', {"fields": ("updated_at",), "classes": ("collapse",)}),
    )

    @admin.display(description='Status', ordering="status")
    def status_badge(self, obj):
        return status_badge(obj.status, obj.get_status_display())

    @admin.display(description='Bilingual content')
    def translation_status(self, obj):
        complete = all(
            [
                obj.title_ne.strip(),
                obj.title_en.strip(),
                obj.content_ne.strip(),
                obj.content_en.strip(),
            ]
        )
        return status_badge(
            "approved" if complete else "needs_review",
            'Complete' if complete else 'Needs translation',
        )

    def has_delete_permission(self, request, obj=None):
        return False
