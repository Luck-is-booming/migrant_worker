from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "name_ne",
        "name_en",
        "membership_type",
        "status",
        "municipality",
        "ward_no",
        "is_public",
    )
    list_filter = (
        "membership_type",
        "status",
        "municipality",
        "level",
        "is_public",
    )
    search_fields = (
        "name_ne",
        "name_en",
        "membership_number",
        "address",
        "phone",
        "designation",
    )
    ordering = ("sort_order", "name_ne")