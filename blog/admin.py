from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'published_date', 'is_alert')
    list_filter = ('is_alert', 'published_date')
    search_fields = ('title_en', 'title_ne', 'content_en', 'content_ne')