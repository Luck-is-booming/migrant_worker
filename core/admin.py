from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html

from migrantcenter.admin_helpers import (
    SuperuserOnlyAdminMixin,
    admin_change_link,
    status_badge,
)

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
    ServiceCard,
    TeamMember,
)


# Human-friendly labels are limited to the admin interface. They do not alter
# database tables, migrations, permissions, or public URLs.
ContactMessage._meta.verbose_name = 'General enquiry'
ContactMessage._meta.verbose_name_plural = 'General enquiries'
Membership._meta.verbose_name = 'Membership application'
Membership._meta.verbose_name_plural = 'Membership applications'
ServiceCard._meta.verbose_name = 'Homepage service'
ServiceCard._meta.verbose_name_plural = 'Homepage services'
TeamMember._meta.verbose_name = 'Committee or team member'
TeamMember._meta.verbose_name_plural = 'Committee and team'


@admin.register(OrganizationInfo)
class OrganizationInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ("chairperson_photo_preview",)
    fieldsets = (
        (
            'Organization identity',
            {
                "fields": (
                    "name_ne",
                    "name_en",
                    "registration_number",
                    "registration_authority_ne",
                    "registration_authority_en",
                    "established_date",
                ),
                "description": 'Use the exact official names and registration details approved by the organization.',
            },
        ),
        (
            'Public message',
            {
                "fields": (
                    "slogan_ne",
                    "slogan_en",
                    "objective_ne",
                    "objective_en",
                    "commitment_ne",
                    "commitment_en",
                    "disclaimer_ne",
                    "disclaimer_en",
                )
            },
        ),
        (
            'Office and contact details',
            {
                "fields": (
                    "official_phone",
                    "official_email",
                    "office_address_ne",
                    "office_address_en",
                    "service_area_ne",
                    "service_area_en",
                    "service_hours_ne",
                    "service_hours_en",
                )
            },
        ),
        (
            "Chairperson's message",
            {
                "fields": (
                    "chairperson_name_ne",
                    "chairperson_name_en",
                    "chairperson_message_ne",
                    "chairperson_message_en",
                    "chairperson_photo",
                    "chairperson_photo_preview",
                ),
                "description": "The saved photo is displayed beside the chairperson's message on the About page.",
            },
        ),
    )

    @admin.display(description='Current chairperson photo')
    def chairperson_photo_preview(self, obj):
        if not obj or not obj.chairperson_photo:
            return 'No chairperson photo has been uploaded.'
        try:
            return format_html(
                '<img class="mrn-admin-preview" src="{}" alt="{}">',
                obj.chairperson_photo.url,
                'Current chairperson photo',
            )
        except (ValueError, OSError):
            return 'The saved image is currently unavailable.'

    def has_add_permission(self, request):
        return not OrganizationInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "masked_phone",
        "subject",
        "status_badge",
        "preferred_language",
        "created_at",
    )
    list_filter = ("status", "preferred_language", "created_at")
    search_fields = ("name", "phone", "email", "subject", "message")
    readonly_fields = ("consent_recorded_at", "source_ip_hash", "created_at")
    date_hierarchy = "created_at"
    list_per_page = 30
    save_on_top = True
    actions = ("mark_reviewed", "mark_closed", "mark_spam")

    fieldsets = (
        ('Person and contact', {"fields": ("name", "phone", "email", "preferred_language")}),
        ('Message', {"fields": ("subject", "message", "consent_to_contact", "consent_recorded_at")}),
        ('What staff should do', {"fields": ("status",)}),
        ('Technical record', {"fields": ("source_ip_hash", "created_at"), "classes": ("collapse",)}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if not request.user.is_superuser:
            fieldsets = [item for item in fieldsets if item[0] != 'Technical record']
        return tuple(fieldsets)

    @admin.display(description='Status', ordering="status")
    def status_badge(self, obj):
        return status_badge(obj.status, obj.get_status_display())

    @admin.display(description='Phone')
    def masked_phone(self, obj):
        return f"••••••{obj.phone[-4:]}" if obj.phone else "—"

    @admin.action(description='Mark selected enquiries as reviewed')
    def mark_reviewed(self, request, queryset):
        queryset.filter(status="new").update(status="reviewed")

    @admin.action(description='Close selected enquiries')
    def mark_closed(self, request, queryset):
        queryset.exclude(status="spam").update(status="closed")

    @admin.action(description='Mark selected enquiries as spam')
    def mark_spam(self, request, queryset):
        queryset.update(status="spam")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Membership)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "name",
        "municipality",
        "membership_type",
        "payment_status_badge",
        "approval_status_badge",
        "joined_date",
    )
    list_filter = (
        "municipality",
        "membership_type",
        "payment_status",
        "is_approved",
        "joined_date",
    )
    search_fields = (
        "public_id",
        "name",
        "name_en",
        "phone",
        "email",
        "transaction_id",
        "normalized_membership__membership_number",
    )
    readonly_fields = (
        "public_id",
        "joined_date",
        "consent_recorded_at",
        "source_ip_hash",
        "payment_status",
        "is_approved",
        "transaction_id",
        "amount",
        "payment_review_link",
        "issued_membership_link",
        "person_record_link",
    )
    list_per_page = 30
    save_on_top = True

    fieldsets = (
        (
            'Applicant',
            {
                "fields": (
                    "public_id",
                    "name",
                    "name_en",
                    "email",
                    "phone",
                    "municipality",
                    "ward_no",
                    "address",
                )
            },
        ),
        (
            'Requested membership',
            {"fields": ("membership_type", "designation", "destination_country", "joined_date")},
        ),
        (
            'Application progress',
            {
                "fields": (
                    "payment_status",
                    "is_approved",
                    "amount",
                    "transaction_id",
                    "payment_review_link",
                    "person_record_link",
                    "issued_membership_link",
                ),
                "description": 'Follow the links below instead of searching across different admin sections.',
            },
        ),
        (
            'Consent and technical record',
            {
                "fields": ("consent_to_privacy", "consent_recorded_at", "source_ip_hash"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("manual_payments")

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if not request.user.is_superuser:
            fieldsets = [
                item for item in fieldsets if item[0] != 'Consent and technical record'
            ]
        return tuple(fieldsets)

    @admin.display(description='Reference')
    def reference(self, obj):
        return str(obj.public_id)[:8]

    @admin.display(description='Payment', ordering="payment_status")
    def payment_status_badge(self, obj):
        return status_badge(obj.payment_status, obj.get_payment_status_display())

    @admin.display(description='Application', ordering="is_approved")
    def approval_status_badge(self, obj):
        return status_badge(
            "approved" if obj.is_approved else "pending",
            'Approved' if obj.is_approved else 'Waiting',
        )

    @admin.display(description='Payment review')
    def payment_review_link(self, obj):
        if not obj or not obj.pk:
            return "—"
        payment = obj.manual_payments.order_by("-submitted_at").first()
        if not payment:
            return 'No payment proof has been submitted.'
        return admin_change_link(payment, 'Open payment review')

    def _issued_membership(self, obj):
        if not obj or not obj.pk:
            return None
        try:
            return obj.normalized_membership
        except (AttributeError, ObjectDoesNotExist):
            return None

    @admin.display(description='Person record')
    def person_record_link(self, obj):
        membership = self._issued_membership(obj)
        return admin_change_link(
            membership.person if membership else None,
            'Open person record' if membership else None,
        )

    @admin.display(description='Issued membership')
    def issued_membership_link(self, obj):
        membership = self._issued_membership(obj)
        if not membership:
            return 'A membership has not been issued yet.'
        return admin_change_link(
            membership,
            f"{membership.membership_number or 'Open issued membership'}",
        )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MembershipPaymentSettings)
class MembershipPaymentSettingsAdmin(admin.ModelAdmin):
    save_on_top = True
    fieldsets = (
        ('Official membership fees', {"fields": ("general_member_amount", "life_member_amount")}),
        (
            'Verified payment destination',
            {
                "fields": (
                    "recipient_name",
                    "payment_qr",
                    "qr_preview",
                    "account_details_ne",
                    "account_details_en",
                )
            },
        ),
        ('Instructions shown to applicants', {"fields": ("instructions_ne", "instructions_en")}),
        (
            'Publish payment details',
            {
                "fields": ("is_active", "readiness", "updated_at"),
                "description": 'Enable only after scanning the QR and confirming the recipient and both fees.',
            },
        ),
    )
    readonly_fields = ("qr_preview", "readiness", "updated_at")

    def has_add_permission(self, request):
        return not MembershipPaymentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Current QR preview')
    def qr_preview(self, obj):
        if not obj or not obj.payment_qr:
            return 'No official QR uploaded.'
        try:
            return format_html(
                '<img class="mrn-admin-preview" src="{}" alt="{}">',
                obj.payment_qr.url,
                'Official payment QR preview',
            )
        except (ValueError, OSError):
            return 'The QR image is unavailable.'

    @admin.display(description='Readiness')
    def readiness(self, obj):
        if not obj:
            return 'Save the settings to check readiness.'
        if obj.is_ready:
            return status_badge("approved", 'Ready for public payment')
        return status_badge(
            "needs_review",
            'Not ready — verify fees, recipient, QR and activation'        )


@admin.register(ServiceCard)
class ServiceCardAdmin(admin.ModelAdmin):
    list_display = ("title_en", "title_ne", "icon_name", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("title_en", "title_ne", "desc_en", "desc_ne")
    fieldsets = (
        ('Title', {"fields": ("title_ne", "title_en")}),
        ('Short explanation', {"fields": ("desc_ne", "desc_en")}),
        ('Optional process details', {"fields": ("process_ne", "process_en"), "classes": ("collapse",)}),
        ('Display', {"fields": ("icon_name", "display_order", "is_active")}),
    )


@admin.register(DestinationCountry)
class DestinationCountryAdmin(SuperuserOnlyAdminMixin, admin.ModelAdmin):
    """Retained for compatibility; it is not part of the normal staff workflow."""

    list_display = ("name_en", "estimated_cost", "last_reviewed", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name_en", "name_ne")


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ne", "slug", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    prepopulated_fields = {"slug": ("name_en",)}
    search_fields = ("name_en", "name_ne", "slug")


@admin.register(OfficialResource)
class OfficialResourceAdmin(admin.ModelAdmin):
    list_display = (
        "title_en",
        "category",
        "is_official_source",
        "language",
        "last_reviewed",
        "is_active",
    )
    list_filter = ("category", "is_official_source", "language", "is_active")
    list_editable = ("is_active",)
    search_fields = ("title_en", "title_ne", "description_en", "description_ne", "url")
    save_on_top = True


@admin.register(EmergencyResource)
class EmergencyResourceAdmin(admin.ModelAdmin):
    list_display = ("title_en", "phone", "last_reviewed", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("title_en", "title_ne", "phone")


@admin.register(FrequentlyAskedQuestion)
class FrequentlyAskedQuestionAdmin(admin.ModelAdmin):
    list_display = ("question_en", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("question_en", "question_ne", "answer_en", "answer_ne")
    save_on_top = True


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = (
        "name_en",
        "name_ne",
        "designation_en",
        "translation_status",
        "sort_order",
        "is_active",
    )
    list_editable = ("sort_order", "is_active")
    search_fields = (
        "name_en",
        "name_ne",
        "designation_en",
        "designation_ne",
        "address_en",
        "address_ne",
        "phone",
        "email",
    )
    readonly_fields = ("image_preview",)
    fieldsets = (
        ('Name and role', {"fields": ("name_ne", "name_en", "designation_ne", "designation_en")}),
        ('Public profile', {"fields": ("address_ne", "address_en", "image", "image_preview")}),
        ('Internal contact', {"fields": ("phone", "email"), "classes": ("collapse",)}),
        ('Publishing', {"fields": ("sort_order", "is_active")}),
    )

    @admin.display(description='Current photo')
    def image_preview(self, obj):
        if not obj or not obj.image:
            return 'No photo uploaded.'
        try:
            return format_html(
                '<img class="mrn-admin-preview" src="{}" alt="{}">',
                obj.image.url,
                obj.name_en or obj.name_ne or 'Team member photo',
            )
        except (ValueError, OSError):
            return 'The saved image is currently unavailable.'

    @admin.display(description='Translation')
    def translation_status(self, obj):
        return status_badge(
            "approved" if obj.translation_complete else "needs_review",
            'Complete' if obj.translation_complete else 'Needs review',
        )
