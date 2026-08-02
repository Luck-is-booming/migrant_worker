from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    ImportBatch,
    ImportRowRecord,
    Member,
    MembershipCategory,
    MembershipNumberIssue,
    MembershipNumberSequence,
    MembershipRecord,
    OrganizationUnit,
    Person,
    PotentialDuplicate,
)
from .services import merge_people


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
    readonly_fields = ("membership_number", "public_designation", "translation_complete")
    show_change_link = True
    can_delete = False


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "membership_count",
        "masked_phone",
        "location",
        "needs_identity_review",
        "is_public",
        "merged_into",
    )
    list_filter = ("needs_identity_review", "is_public")
    search_fields = (
        "name_ne",
        "name_en",
        "phone",
        "email",
        "memberships__membership_number",
        "memberships__organization_unit__name_en",
    )
    readonly_fields = (
        "public_id",
        "normalized_name",
        "merged_into",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        ("Identity", {"fields": ("public_id", "name_ne", "name_en", "normalized_name")}),
        ("Private contact", {"fields": ("phone", "email", "location"), "description": "These fields are never shown in the public directory."}),
        ("Review and publication", {"fields": ("needs_identity_review", "is_public", "merged_into")}),
        ("Audit", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    inlines = [MembershipInline]
    actions = ("hide_from_public_directory", "restore_to_public_directory")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_membership_count=Count("memberships"))

    @admin.display(ordering="_membership_count", description="Memberships")
    def membership_count(self, obj):
        return obj._membership_count

    @admin.display(description="Phone")
    def masked_phone(self, obj):
        if not obj.phone:
            return "—"
        return f"••••••{obj.phone[-4:]}"

    @admin.action(description="Hide selected people from the public directory")
    def hide_from_public_directory(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f"Hidden {updated} person record(s).", messages.SUCCESS)

    @admin.action(description="Restore selected people to the public directory")
    def restore_to_public_directory(self, request, queryset):
        updated = queryset.filter(merged_into__isnull=True).update(is_public=True)
        self.message_user(request, f"Restored {updated} person record(s).", messages.SUCCESS)

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
        "is_public",
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
    autocomplete_fields = (
        "person",
        "category",
        "organization_unit",
        "legacy_member",
        "source_application",
    )
    fieldsets = (
        ("Membership", {"fields": ("person", "category", "organization_unit", "membership_number", "status", "joined_date")}),
        ("Public profile — Nepali", {"fields": ("designation_ne", "destination_country_ne", "address_display_ne")}),
        ("Public profile — English", {"fields": ("designation_en", "destination_country_en", "address_display_en")}),
        ("Publication", {"fields": ("translation_complete", "is_public")}),
        ("Original imported values", {"fields": ("designation", "destination_country", "address_display"), "classes": ("collapse",), "description": "Read-only source values retained for audit. Edit the bilingual public fields above."}),
        ("Source links", {"fields": ("legacy_member", "source_application", "created_by_import"), "classes": ("collapse",)}),
        ("Archive and audit", {"fields": ("public_id", "membership_number_normalized", "membership_number_int", "archived_at", "archived_by", "was_public_before_archive", "created_at", "updated_at"), "classes": ("collapse",)}),
    )
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
    )
    actions = ("archive_memberships", "restore_memberships")

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj:
            fields.append("membership_number")
        return tuple(fields)


    @admin.display(boolean=True, description="Bilingual public fields complete")
    def translation_status(self, obj):
        return obj.translation_complete

    @admin.display(description="Status")
    def status_badge(self, obj):
        styles = {
            "active": "background:#dcfce7;color:#166534",
            "inactive": "background:#e2e8f0;color:#334155",
            "pending": "background:#fef3c7;color:#92400e",
            "expired": "background:#ffedd5;color:#9a3412",
            "suspended": "background:#fee2e2;color:#991b1b",
            "archived": "background:#e2e8f0;color:#334155",
            "rejected": "background:#fee2e2;color:#991b1b",
        }
        return format_html(
            '<span style="{};padding:3px 8px;border-radius:999px;font-weight:600">{}</span>',
            styles.get(obj.status, styles["inactive"]),
            obj.get_status_display(),
        )

    @admin.action(description="Archive selected memberships")
    def archive_memberships(self, request, queryset):
        count = 0
        for membership in queryset:
            if membership.status != "archived":
                membership.archive(user=request.user)
                count += 1
        self.message_user(request, f"Archived {count} membership(s).", messages.SUCCESS)

    @admin.action(description="Restore selected archived memberships")
    def restore_memberships(self, request, queryset):
        count = 0
        for membership in queryset:
            if membership.status == "archived":
                membership.restore()
                count += 1
        self.message_user(request, f"Restored {count} membership(s).", messages.SUCCESS)

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
class MembershipNumberSequenceAdmin(admin.ModelAdmin):
    list_display = ("organization_unit", "category", "next_number", "updated_at")
    list_filter = ("category", "organization_unit")
    search_fields = ("organization_unit__name_en", "category__name_en")
    readonly_fields = ("category", "organization_unit", "next_number", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MembershipNumberIssue)
class MembershipNumberIssueAdmin(admin.ModelAdmin):
    list_display = ("membership_number", "category", "organization_unit", "source", "membership", "issued_at")
    list_filter = ("source", "category", "organization_unit", "issued_at")
    search_fields = ("membership_number", "organization_unit__name_en", "membership__person__name_en", "membership__person__name_ne")
    readonly_fields = (
        "category", "organization_unit", "membership_number", "membership_number_normalized",
        "number_int", "membership", "source", "issued_by", "issued_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ImportRowInline(admin.TabularInline):
    model = ImportRowRecord
    extra = 0
    can_delete = False
    fields = ("row_number", "status", "person", "membership", "warnings", "error_message")
    readonly_fields = fields
    max_num = 0


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("source_file_name", "source_sheet", "status", "is_dry_run", "started_at", "completed_at")
    list_filter = ("status", "is_dry_run", "started_at")
    search_fields = ("source_file_name", "source_checksum", "public_id")
    readonly_fields = (
        "public_id", "source_file_name", "source_checksum", "source_sheet", "status",
        "is_dry_run", "options", "summary", "started_at", "completed_at", "created_by",
    )
    inlines = [ImportRowInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PotentialDuplicate)
class PotentialDuplicateAdmin(admin.ModelAdmin):
    list_display = ("person_a", "person_b", "status", "signals", "created_at", "reviewed_by")
    list_filter = ("status", "created_at")
    search_fields = ("person_a__name_ne", "person_b__name_ne", "person_a__phone", "person_b__phone")
    readonly_fields = ("signals", "created_at", "reviewed_by", "reviewed_at")
    actions = ("mark_different", "merge_b_into_a")

    @admin.action(description="Confirm selected pairs are different people")
    def mark_different(self, request, queryset):
        updated = queryset.update(status="different", reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f"Marked {updated} pair(s) as different people.", messages.SUCCESS)

    @admin.action(description="Preview and merge person B into person A")
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
                    "title": "Confirm person merges",
                    "pairs": queryset,
                    "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
                    "action_name": "merge_b_into_a",
                    "opts": self.model._meta,
                },
            )

        merged = 0
        for review in queryset:
            try:
                merge_people(canonical=review.person_a, duplicate=review.person_b, reviewed_by=request.user)
                merged += 1
            except ValueError as exc:
                self.message_user(request, f"Could not merge {review}: {exc}", messages.ERROR)
        if merged:
            self.message_user(request, f"Merged {merged} reviewed pair(s).", messages.SUCCESS)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Member)
class LegacyMemberAdmin(admin.ModelAdmin):
    list_display = ("name_ne", "level", "unit_name", "membership_type", "membership_number", "status", "is_public")
    list_filter = ("level", "unit_name", "membership_type", "status", "is_public")
    search_fields = ("name_ne", "name_en", "membership_number", "phone")
    readonly_fields = ("source_membership", "membership_number", "membership_number_int", "created_at")
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
