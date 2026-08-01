from django.contrib import admin

from .models import (
    ContactMessage,
    DestinationCountry,
    EmergencyResource,
    FrequentlyAskedQuestion,
    Membership,
    OfficialResource,
    OrganizationInfo,
    ResourceCategory,
    ResourcePublication,
    ServiceCard,
    TeamMember,
)


@admin.register(OrganizationInfo)
class OrganizationInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identity", {"fields": ("name_ne", "name_en", "registration_number", "established_date")}),
        ("Positioning", {"fields": ("slogan_ne", "slogan_en", "objective_ne", "objective_en", "commitment_ne", "commitment_en", "disclaimer_ne", "disclaimer_en")}),
        ("Public contact", {"fields": ("official_phone", "official_email", "office_address_ne", "office_address_en", "service_hours_ne", "service_hours_en")}),
        ("Chairperson", {"fields": ("chairperson_name_ne", "chairperson_name_en", "chairperson_message_ne", "chairperson_message_en", "chairperson_photo")}),
    )

    def has_add_permission(self, request):
        return not OrganizationInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "masked_phone", "subject", "status", "preferred_language", "created_at")
    list_filter = ("status", "preferred_language", "created_at")
    search_fields = ("name", "phone", "email", "subject")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    @admin.display(description="Phone")
    def masked_phone(self, obj):
        return f"••••••{obj.phone[-4:]}" if obj.phone else "—"


@admin.register(Membership)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "municipality", "membership_type", "payment_status", "is_approved", "joined_date")
    list_filter = ("municipality", "membership_type", "payment_status", "is_approved")
    search_fields = ("name", "name_en", "phone", "email", "transaction_id")
    readonly_fields = ("joined_date",)


@admin.register(ServiceCard)
class ServiceCardAdmin(admin.ModelAdmin):
    list_display = ("title_en", "icon_name", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("title_en", "title_ne", "desc_en", "desc_ne")


@admin.register(DestinationCountry)
class DestinationCountryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "estimated_cost", "last_reviewed", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name_en", "name_ne")


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ne", "slug", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(OfficialResource)
class OfficialResourceAdmin(admin.ModelAdmin):
    list_display = ("title_en", "category", "is_official_source", "language", "last_reviewed", "is_active")
    list_filter = ("category", "is_official_source", "language", "is_active")
    list_editable = ("is_active",)
    search_fields = ("title_en", "title_ne", "description_en", "description_ne", "url")


@admin.register(EmergencyResource)
class EmergencyResourceAdmin(admin.ModelAdmin):
    list_display = ("title_en", "phone", "last_reviewed", "display_order", "is_active")
    list_editable = ("display_order", "is_active")


@admin.register(FrequentlyAskedQuestion)
class FrequentlyAskedQuestionAdmin(admin.ModelAdmin):
    list_display = ("question_en", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("question_en", "question_ne", "answer_en", "answer_ne")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "designation", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "designation", "address")


@admin.register(ResourcePublication)
class LegacyResourcePublicationAdmin(admin.ModelAdmin):
    list_display = ("title_en", "download_url")

    def has_delete_permission(self, request, obj=None):
        return False
