from django.contrib import admin

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "level",
        "unit_name",
        "membership_type",
        "membership_number",
        "name_ne",
        "name_en",
        "municipality",
        "address",
        "designation",
        "status",
        "is_public",
    )
    list_display_links = ("name_ne",)
    list_editable = ("membership_number", "status", "is_public")
    search_fields = (
        "name_ne",
        "name_en",
        "membership_number",
        "unit_name",
        "municipality",
        "address",
        "designation",
        "destination_country",
        "phone",
    )
    list_filter = (
        "level",
        "unit_name",
        "membership_type",
        "status",
        "municipality",
        "is_public",
    )
    ordering = (
        "level",
        "unit_name",
        "membership_type",
        "membership_number_int",
        "sort_order",
        "name_ne",
    )
    fields = (
        "name_ne",
        "name_en",
        "membership_number",
        "membership_type",
        "status",
        "level",
        "unit_name",
        "municipality",
        "address",
        "designation",
        "destination_country",
        "phone",
        "show_phone_publicly",
        "is_public",
        "sort_order",
    )
