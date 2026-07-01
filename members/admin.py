from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
    "name_ne",
    "membership_number",
    "level",
    "unit_name",
    "membership_type",
    "status",
    "is_public",
)
    list_filter = (
        "level",
        "unit_name",
        "membership_type",
        "status",
        "is_public",
    )

    search_fields = (
        "name_ne",
        "name_en",
        "membership_number",
        "unit_name",
        "address",
        "phone",
        "designation",
    )
    ordering = ("sort_order", "name_ne")