from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.db.models import Count
from django.utils import timezone
from django.template.response import TemplateResponse
from django.utils.html import format_html

from .models import (
    ImportBatch,
    ImportRowRecord,
    Member,
    MembershipCategory,
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
        "designation",
        "is_public",
    )
    show_change_link = True


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
        "memberships__membership_number",
        "memberships__organization_unit__name_en",
    )
    readonly_fields = ("public_id", "normalized_name", "merged_into", "created_at", "updated_at")
    inlines = [MembershipInline]

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


@admin.register(MembershipRecord)
class MembershipRecordAdmin(admin.ModelAdmin):
    list_display = (
        "person",
        "category",
        "organization_unit",
        "membership_number",
        "status_badge",
        "is_public",
        "updated_at",
    )
    list_filter = ("category", "organization_unit", "status", "is_public")
    search_fields = (
        "person__name_ne",
        "person__name_en",
        "membership_number",
        "organization_unit__name_en",
        "designation",
    )
    autocomplete_fields = ("person", "category", "organization_unit", "legacy_member", "source_application")
    readonly_fields = (
        "public_id",
        "membership_number_normalized",
        "membership_number_int",
        "created_by_import",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        styles = {
            "active": "background:#dcfce7;color:#166534",
            "expired": "background:#fef3c7;color:#92400e",
            "archived": "background:#e2e8f0;color:#334155",
            "unknown": "background:#f1f5f9;color:#475569",
        }
        return format_html(
            '<span style="{};padding:3px 8px;border-radius:999px;font-weight:600">{}</span>',
            styles.get(obj.status, styles["unknown"]),
            obj.get_status_display(),
        )


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
    inlines = [ImportRowInline]


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
                merge_people(
                    canonical=review.person_a,
                    duplicate=review.person_b,
                    reviewed_by=request.user,
                )
                merged += 1
            except ValueError as exc:
                self.message_user(
                    request, f"Could not merge {review}: {exc}", messages.ERROR
                )
        if merged:
            self.message_user(
                request, f"Merged {merged} reviewed pair(s).", messages.SUCCESS
            )


@admin.register(Member)
class LegacyMemberAdmin(admin.ModelAdmin):
    list_display = (
        "name_ne",
        "level",
        "unit_name",
        "membership_type",
        "membership_number",
        "status",
        "is_public",
    )
    list_filter = ("level", "unit_name", "membership_type", "status", "is_public")
    search_fields = ("name_ne", "name_en", "membership_number", "phone")
    readonly_fields = ("source_membership", "created_at")
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False
