from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils import timezone

from migrantcenter.admin_helpers import (
    SuperuserReadOnlyAdminMixin,
    admin_change_link,
    status_badge,
)

from .models import (
    ImportBatch,
    ImportRowRecord,
    MembershipCategory,
    MembershipNumberIssue,
    MembershipNumberSequence,
    MembershipRecord,
    OrganizationUnit,
    Person,
    PotentialDuplicate,
)
from .services import merge_people


Person._meta.verbose_name = 'Person'
Person._meta.verbose_name_plural = 'People'
MembershipRecord._meta.verbose_name = 'Issued membership'
MembershipRecord._meta.verbose_name_plural = 'Issued memberships'
OrganizationUnit._meta.verbose_name = 'Membership unit'
OrganizationUnit._meta.verbose_name_plural = 'Membership units'
PotentialDuplicate._meta.verbose_name = 'Duplicate review'
PotentialDuplicate._meta.verbose_name_plural = 'Duplicate reviews'
MembershipNumberIssue._meta.verbose_name = 'Membership number audit entry'
MembershipNumberIssue._meta.verbose_name_plural = 'Membership number audit'
ImportBatch._meta.verbose_name = 'Member import batch'
ImportBatch._meta.verbose_name_plural = 'Member import history'


class MembershipInline(admin.TabularInline):
    model = MembershipRecord
    extra = 0
    fields = (
        "category",
        "organization_unit",
        "membership_number",
        "status",
        "public_designation",
        "translation_complete",
        "is_public",
    )
    readonly_fields = (
        "membership_number",
        "public_designation",
        "translation_complete",
    )
    show_change_link = True
    can_delete = False
    verbose_name = 'Issued membership'
    verbose_name_plural = 'Memberships held by this person'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "membership_count",
        "masked_phone",
        "location",
        "identity_review_badge",
        "public_badge",
    )
    list_filter = ("needs_identity_review", "is_public")
    search_fields = (
        "name_ne",
        "name_en",
        "phone",
        "email",
        "memberships__membership_number",
        "memberships__organization_unit__name_en",
        "memberships__organization_unit__name_ne",
    )
    readonly_fields = (
        "public_id",
        "normalized_name",
        "merged_into",
        "created_at",
        "updated_at",
    )
    inlines = (MembershipInline,)
    actions = ("hide_from_public_directory", "restore_to_public_directory")
    list_per_page = 30
    save_on_top = True

    fieldsets = (
        ('Name', {"fields": ("name_ne", "name_en")}),
        (
            'Private contact details',
            {
                "fields": ("phone", "email", "location"),
                "description": 'These details are never shown in the public member directory.',
            },
        ),
        (
            'Review and public visibility',
            {
                "fields": ("needs_identity_review", "is_public"),
                "description": 'Hide the person only when their public profile must not be shown. Their membership numbers remain preserved.',
            },
        ),
        (
            'Technical and merge record',
            {
                "fields": (
                    "public_id",
                    "normalized_name",
                    "merged_into",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if not request.user.is_superuser:
            fieldsets = [
                item for item in fieldsets if item[0] != 'Technical and merge record'
            ]
        return tuple(fieldsets)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_membership_count=Count("memberships", distinct=True))

    @admin.display(ordering="_membership_count", description='Memberships')
    def membership_count(self, obj):
        return obj._membership_count

    @admin.display(description='Phone')
    def masked_phone(self, obj):
        if not obj.phone:
            return "—"
        return f"••••••{obj.phone[-4:]}"

    @admin.display(description='Identity review', ordering="needs_identity_review")
    def identity_review_badge(self, obj):
        return status_badge(
            "needs_review" if obj.needs_identity_review else "approved",
            'Needs review' if obj.needs_identity_review else 'Checked',
        )

    @admin.display(description='Public', ordering="is_public")
    def public_badge(self, obj):
        return status_badge(
            "active" if obj.is_public and not obj.merged_into_id else "inactive",
            'Shown' if obj.is_public and not obj.merged_into_id else 'Hidden',
        )

    @admin.action(description='Hide selected people from the public directory')
    def hide_from_public_directory(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(
            request,
            'Hidden %(count)s person record(s).' % {"count": updated},
            messages.SUCCESS,
        )

    @admin.action(description='Restore selected people to the public directory')
    def restore_to_public_directory(self, request, queryset):
        updated = queryset.filter(merged_into__isnull=True).update(is_public=True)
        self.message_user(
            request,
            'Restored %(count)s person record(s).' % {"count": updated},
            messages.SUCCESS,
        )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MembershipRecord)
class MembershipRecordAdmin(admin.ModelAdmin):
    list_display = (
        "person",
        "category",
        "organization_unit",
        "membership_number",
        "status_badge",
        "translation_status",
        "public_badge",
        "updated_at",
    )
    list_filter = ("category", "organization_unit", "status", "is_public")
    list_select_related = ("person", "category", "organization_unit", "archived_by")
    search_fields = (
        "person__name_ne",
        "person__name_en",
        "membership_number",
        "organization_unit__name_en",
        "organization_unit__name_ne",
        "designation_ne",
        "designation_en",
        "destination_country_ne",
        "destination_country_en",
        "address_display_ne",
        "address_display_en",
    )
    autocomplete_fields = ("person", "category", "organization_unit")
    readonly_fields = (
        "public_id",
        "translation_complete",
        "designation",
        "destination_country",
        "address_display",
        "membership_number_normalized",
        "membership_number_int",
        "created_by_import",
        "archived_at",
        "archived_by",
        "was_public_before_archive",
        "created_at",
        "updated_at",
        "source_application_link",
        "payment_review_link",
        "legacy_member",
    )
    actions = ("archive_memberships", "restore_memberships")
    list_per_page = 30
    save_on_top = True

    fieldsets = (
        (
            'Membership',
            {
                "fields": (
                    "person",
                    "category",
                    "organization_unit",
                    "membership_number",
                    "status",
                    "joined_date",
                )
            },
        ),
        ('Public profile — Nepali', {"fields": ("designation_ne", "destination_country_ne", "address_display_ne")}),
        ('Public profile — English', {"fields": ("designation_en", "destination_country_en", "address_display_en")}),
        (
            'Public visibility',
            {
                "fields": ("translation_complete", "is_public"),
                "description": 'A person can hold more than one membership. Only non-sensitive public details are displayed.',
            },
        ),
        (
            'Related application and payment',
            {
                "fields": ("source_application_link", "payment_review_link"),
                "classes": ("collapse",),
            },
        ),
        (
            'Original imported values',
            {
                "fields": ("designation", "destination_country", "address_display"),
                "classes": ("collapse",),
                "description": 'Read-only source values retained for checking imports. Edit the bilingual fields above.',
            },
        ),
        (
            'Technical and audit record',
            {
                "fields": (
                    "legacy_member",
                    "created_by_import",
                    "public_id",
                    "membership_number_normalized",
                    "membership_number_int",
                    "archived_at",
                    "archived_by",
                    "was_public_before_archive",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if not request.user.is_superuser:
            hidden = {'Original imported values', 'Technical and audit record'}
            fieldsets = [item for item in fieldsets if item[0] not in hidden]
        return tuple(fieldsets)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj:
            fields.append("membership_number")
        return tuple(fields)

    @admin.display(description='Bilingual public fields')
    def translation_status(self, obj):
        return status_badge(
            "approved" if obj.translation_complete else "needs_review",
            'Complete' if obj.translation_complete else 'Needs review',
        )

    @admin.display(description='Status', ordering="status")
    def status_badge(self, obj):
        return status_badge(obj.status, obj.get_status_display())

    @admin.display(description='Public', ordering="is_public")
    def public_badge(self, obj):
        return status_badge(
            "active" if obj.is_public and obj.status != "archived" else "inactive",
            'Shown' if obj.is_public and obj.status != "archived" else 'Hidden',
        )

    @admin.display(description='Membership application')
    def source_application_link(self, obj):
        if not obj or not obj.source_application_id:
            return 'This membership was not created from an online application.'
        return admin_change_link(obj.source_application, 'Open membership application')

    @admin.display(description='Payment review')
    def payment_review_link(self, obj):
        if not obj or not obj.source_application_id:
            return "—"
        payment = obj.source_application.manual_payments.order_by("-submitted_at").first()
        if not payment:
            return 'No payment review is linked.'
        return admin_change_link(payment, 'Open payment review')

    @admin.action(description='Archive selected memberships')
    def archive_memberships(self, request, queryset):
        count = 0
        for membership in queryset:
            if membership.status != "archived":
                membership.archive(user=request.user)
                count += 1
        self.message_user(
            request,
            'Archived %(count)s membership(s).' % {"count": count},
            messages.SUCCESS,
        )

    @admin.action(description='Restore selected archived memberships')
    def restore_memberships(self, request, queryset):
        count = 0
        for membership in queryset:
            if membership.status == "archived":
                membership.restore()
                count += 1
        self.message_user(
            request,
            'Restored %(count)s membership(s).' % {"count": count},
            messages.SUCCESS,
        )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MembershipCategory)
class MembershipCategoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ne", "code", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("name_en", "name_ne", "code")


@admin.register(OrganizationUnit)
class OrganizationUnitAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ne", "level", "parent", "is_active", "display_order")
    list_filter = ("level", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("name_en", "name_ne", "geographic_name")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(MembershipNumberSequence)
class MembershipNumberSequenceAdmin(SuperuserReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("organization_unit", "category", "next_number", "updated_at")
    list_filter = ("category", "organization_unit")
    search_fields = ("organization_unit__name_en", "category__name_en")
    readonly_fields = ("category", "organization_unit", "next_number", "updated_at")


@admin.register(MembershipNumberIssue)
class MembershipNumberIssueAdmin(SuperuserReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        "membership_number",
        "category",
        "organization_unit",
        "source",
        "membership",
        "issued_at",
    )
    list_filter = ("source", "category", "organization_unit", "issued_at")
    search_fields = (
        "membership_number",
        "organization_unit__name_en",
        "membership__person__name_en",
        "membership__person__name_ne",
    )
    readonly_fields = (
        "category",
        "organization_unit",
        "membership_number",
        "membership_number_normalized",
        "number_int",
        "membership",
        "source",
        "issued_by",
        "issued_at",
    )


class ImportRowInline(admin.TabularInline):
    model = ImportRowRecord
    extra = 0
    can_delete = False
    fields = ("row_number", "status", "person", "membership", "warnings", "error_message")
    readonly_fields = fields
    max_num = 0


@admin.register(ImportBatch)
class ImportBatchAdmin(SuperuserReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        "source_file_name",
        "source_sheet",
        "status",
        "is_dry_run",
        "started_at",
        "completed_at",
    )
    list_filter = ("status", "is_dry_run", "started_at")
    search_fields = ("source_file_name", "source_checksum", "public_id")
    readonly_fields = (
        "public_id",
        "source_file_name",
        "source_checksum",
        "source_sheet",
        "status",
        "is_dry_run",
        "options",
        "summary",
        "started_at",
        "completed_at",
        "created_by",
    )
    inlines = (ImportRowInline,)


@admin.register(PotentialDuplicate)
class PotentialDuplicateAdmin(admin.ModelAdmin):
    list_display = (
        "person_a_link",
        "person_b_link",
        "status_badge",
        "signals",
        "created_at",
        "reviewed_by",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "person_a__name_ne",
        "person_a__name_en",
        "person_b__name_ne",
        "person_b__name_en",
        "person_a__phone",
        "person_b__phone",
    )
    readonly_fields = (
        "person_a_link",
        "person_b_link",
        "signals",
        "created_at",
        "reviewed_by",
        "reviewed_at",
    )
    fields = (
        "person_a_link",
        "person_b_link",
        "signals",
        "status",
        "reviewed_by",
        "reviewed_at",
        "created_at",
    )
    actions = ("mark_different", "merge_b_into_a")
    list_per_page = 30

    @admin.display(description='Person A', ordering="person_a")
    def person_a_link(self, obj):
        return admin_change_link(obj.person_a)

    @admin.display(description='Person B', ordering="person_b")
    def person_b_link(self, obj):
        return admin_change_link(obj.person_b)

    @admin.display(description='Status', ordering="status")
    def status_badge(self, obj):
        return status_badge(obj.status, obj.get_status_display())

    @admin.action(description='Confirm selected pairs are different people')
    def mark_different(self, request, queryset):
        updated = queryset.update(
            status="different",
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(
            request,
            'Marked %(count)s pair(s) as different people.' % {"count": updated},
            messages.SUCCESS,
        )

    @admin.action(description='Preview and merge person B into person A')
    def merge_b_into_a(self, request, queryset):
        queryset = queryset.select_related("person_a", "person_b").prefetch_related(
            "person_a__memberships__category",
            "person_a__memberships__organization_unit",
            "person_b__memberships__category",
            "person_b__memberships__organization_unit",
        )
        if request.POST.get("confirm") != "yes":
            return TemplateResponse(
                request,
                "admin/members/potentialduplicate/confirm_merge.html",
                {
                    **self.admin_site.each_context(request),
                    "title": 'Confirm person merges',
                    "pairs": queryset,
                    "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
                    "action_name": "merge_b_into_a",
                    "opts": self.model._meta,
                },
            )

        merged = 0
        for review in queryset:
            try:
                merge_people(
                    canonical=review.person_a,
                    duplicate=review.person_b,
                    reviewed_by=request.user,
                )
                merged += 1
            except ValueError as exc:
                self.message_user(
                    request,
                    'Could not merge %(review)s: %(error)s'
                    % {"review": review, "error": exc},
                    messages.ERROR,
                )
        if merged:
            self.message_user(
                request,
                'Merged %(count)s reviewed pair(s).' % {"count": merged},
                messages.SUCCESS,
            )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
