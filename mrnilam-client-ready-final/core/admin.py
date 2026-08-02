from django.contrib import admin
from django.utils.html import format_html

from .models import (
    ContactMessage,
    DestinationCountry,
    EmergencyResource,
    FrequentlyAskedQuestion,
    Membership,
    MembershipPaymentSettings,
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
        ("Identity", {"fields": ("name_ne", "name_en", "registration_number", "registration_authority_ne", "registration_authority_en", "established_date")}),
        ("Positioning", {"fields": ("slogan_ne", "slogan_en", "objective_ne", "objective_en", "commitment_ne", "commitment_en", "disclaimer_ne", "disclaimer_en")}),
        ("Public contact", {"fields": ("official_phone", "official_email", "office_address_ne", "office_address_en", "service_area_ne", "service_area_en", "service_hours_ne", "service_hours_en")}),
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
    readonly_fields = ("consent_recorded_at", "source_ip_hash", "created_at")
    fieldsets = (
        ("Contact", {"fields": ("name", "phone", "email", "preferred_language")}),
        ("Message", {"fields": ("subject", "message", "consent_to_contact", "consent_recorded_at")}),
        ("Workflow", {"fields": ("status",)}),
        ("Audit", {"fields": ("source_ip_hash", "created_at"), "classes": ("collapse",)}),
    )
    date_hierarchy = "created_at"

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Phone")
    def masked_phone(self, obj):
        return f"••••••{obj.phone[-4:]}" if obj.phone else "—"


@admin.register(Membership)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "municipality", "membership_type", "payment_status", "is_approved", "joined_date")
    list_filter = ("municipality", "membership_type", "payment_status", "is_approved", "joined_date")
    search_fields = ("public_id", "name", "name_en", "phone", "email", "transaction_id")
    readonly_fields = (
        "public_id", "joined_date", "consent_recorded_at", "source_ip_hash",
        "is_approved", "payment_status", "transaction_id", "amount",
    )
    fieldsets = (
        ("Applicant", {"fields": ("public_id", "name", "name_en", "email", "phone", "municipality", "ward_no", "address")}),
        ("Membership", {"fields": ("membership_type", "designation", "destination_country", "joined_date")}),
        ("Consent and audit", {"fields": ("consent_to_privacy", "consent_recorded_at", "source_ip_hash"), "classes": ("collapse",)}),
        ("Payment result", {"fields": ("payment_status", "is_approved", "transaction_id", "amount")}),
    )

    @admin.display(description="Reference")
    def reference(self, obj):
        return str(obj.public_id)[:8]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MembershipPaymentSettings)
class MembershipPaymentSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Official fees", {"fields": ("general_member_amount", "life_member_amount")}),
        ("Verified payment destination", {"fields": ("recipient_name", "payment_qr", "qr_preview", "account_details_ne", "account_details_en")}),
        ("Instructions", {"fields": ("instructions_ne", "instructions_en")}),
        ("Publishing control", {"fields": ("is_active", "readiness", "updated_at")}),
    )
    readonly_fields = ("qr_preview", "readiness", "updated_at")

    def has_add_permission(self, request):
        return not MembershipPaymentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Current QR preview")
    def qr_preview(self, obj):
        if not obj or not obj.payment_qr:
            return "No official QR uploaded"
        try:
            return format_html(
                '<img src="{}" alt="Official payment QR preview" style="max-width:280px;max-height:280px;object-fit:contain;border:1px solid #ddd;padding:8px">',
                obj.payment_qr.url,
            )
        except (ValueError, OSError):
            return "QR image is unavailable"

    @admin.display(description="Readiness")
    def readiness(self, obj):
        if not obj:
            return "Save the configuration to evaluate readiness."
        return "Ready for public payment" if obj.is_ready else (
            "Not ready: verify fees, recipient name, QR image, and enable the configuration."
        )


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
    list_display = (
        "name_en", "name_ne", "designation_en", "translation_status",
        "sort_order", "is_active",
    )
    list_editable = ("sort_order", "is_active")
    search_fields = (
        "name_en", "name_ne", "designation_en", "designation_ne",
        "address_en", "address_ne", "phone", "email",
    )
    fieldsets = (
        ("Identity", {"fields": ("name_ne", "name_en", "designation_ne", "designation_en")}),
        ("Public details", {"fields": ("address_ne", "address_en", "image")}),
        ("Internal contact", {"fields": ("phone", "email"), "classes": ("collapse",)}),
        ("Publishing", {"fields": ("sort_order", "is_active")}),
    )

    @admin.display(description="Translation")
    def translation_status(self, obj):
        return "Complete" if obj.translation_complete else "Needs English/Nepali review"


@admin.register(ResourcePublication)
class LegacyResourcePublicationAdmin(admin.ModelAdmin):
    list_display = ("title_en", "download_url")

    def has_delete_permission(self, request, obj=None):
        return False
