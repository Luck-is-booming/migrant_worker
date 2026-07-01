from django.contrib import admin
from django.utils.html import mark_safe
from .models import (
    OrganizationInfo,
    ContactMessage,
    Membership,
    ServiceCard,
    DestinationCountry,
    ResourcePublication,
    TeamMember,
)


@admin.register(OrganizationInfo)
class OrganizationInfoAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ne')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('name', 'email', 'subject')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'municipality', 'membership_type', 'is_approved', 'payment_status', 'amount')
    list_editable = ('is_approved',)
    list_filter = ('municipality', 'is_approved', 'payment_status', 'membership_type')
    search_fields = ('name', 'transaction_id')
    readonly_fields = ('joined_date', 'transaction_id')


@admin.register(ServiceCard)
class ServiceCardAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_ne')
    search_fields = ('title_en', 'title_ne')


@admin.register(DestinationCountry)
class DestinationCountryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ne', 'flag_emoji', 'estimated_cost')
    search_fields = ('name_en', 'name_ne')


@admin.register(ResourcePublication)
class ResourcePublicationAdmin(admin.ModelAdmin):
    list_display = ('title_en', 'title_ne', 'file_size')
    search_fields = ('title_en', 'title_ne')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sort_order",
        "designation",
        "address",
        "phone",
        "is_active",
        "photo_preview",
    )
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "designation", "address", "phone")
    list_filter = ("designation", "is_active")
    fields = (
        "name",
        "designation",
        "address",
        "phone",
        "email",
        "image",
        "photo_preview",
        "sort_order",
        "is_active",
    )
    readonly_fields = ("photo_preview",)

    def photo_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="width:70px;height:70px;object-fit:cover;border-radius:50%;" />'
            )
        return "No photo uploaded"

    photo_preview.short_description = "Photo"
