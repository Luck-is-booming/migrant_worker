import mimetypes

from django.contrib import admin
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import ContactAttempt, CounselingCategory, CounselingNote, CounselingRequest


class CounselingNoteInline(admin.TabularInline):
    model = CounselingNote
    extra = 0
    can_delete = False
    fields = ("note", "created_by", "created_at")
    readonly_fields = ("created_by", "created_at",)


class ContactAttemptInline(admin.TabularInline):
    model = ContactAttempt
    extra = 0
    can_delete = False
    fields = ("method", "outcome", "note", "attempted_by", "attempted_at")
    readonly_fields = ("attempted_by", "attempted_at",)


@admin.register(CounselingRequest)
class CounselingRequestAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "full_name", "masked_phone", "category", "status",
        "assigned_to", "created_at", "retention_status",
    )
    list_filter = (
        "status", "retention_status", "category", "preferred_language",
        "preferred_contact_method", "created_at",
    )
    search_fields = ("public_id", "full_name", "phone", "email", "location")
    date_hierarchy = "created_at"
    list_select_related = ("category", "assigned_to")
    autocomplete_fields = ("assigned_to",)
    readonly_fields = (
        "public_id", "consent_recorded_at", "source_ip_hash", "created_at",
        "updated_at", "attachment_preview",
    )
    fieldsets = (
        ("Private requester information", {"fields": ("public_id", "full_name", "phone", "email", "location", "preferred_language")}),
        ("Request", {"fields": ("category", "message", "preferred_contact_method", "availability", "attachment_preview", "consent_to_contact", "consent_recorded_at")}),
        ("Staff workflow", {"fields": ("status", "assigned_to", "internal_summary", "retention_status", "closed_at")}),
        ("Audit", {"fields": ("source_ip_hash", "created_at", "updated_at"), "classes": ("collapse",)}),
    )
    inlines = (CounselingNoteInline, ContactAttemptInline)
    actions = ("mark_reviewed", "mark_spam", "mark_closed")

    def get_urls(self):
        return [
            path(
                "<int:object_id>/attachment/",
                self.admin_site.admin_view(self.attachment_view),
                name="counseling_counselingrequest_attachment",
            )
        ] + super().get_urls()

    def attachment_view(self, request, object_id):
        if not request.user.has_perm("counseling.view_counselingrequest"):
            raise Http404
        obj = get_object_or_404(CounselingRequest, pk=object_id)
        if not obj.attachment:
            raise Http404
        try:
            handle = obj.attachment.open("rb")
        except (OSError, ValueError) as exc:
            raise Http404 from exc
        response = FileResponse(
            handle,
            content_type=mimetypes.guess_type(obj.attachment.name)[0]
            or "application/octet-stream",
        )
        response["Cache-Control"] = "private, no-store"
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

    @admin.display(description="Private attachment")
    def attachment_preview(self, obj):
        if not obj or not obj.attachment:
            return "No attachment"
        url = reverse("admin:counseling_counselingrequest_attachment", args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">Open protected attachment</a>',
            url,
        )

    @admin.display(description="Reference")
    def reference(self, obj):
        return str(obj.public_id)[:8]

    @admin.display(description="Phone")
    def masked_phone(self, obj):
        return f"••••••{obj.phone[-4:]}" if obj.phone else "—"

    @admin.action(description="Mark selected requests reviewed")
    def mark_reviewed(self, request, queryset):
        queryset.filter(status="new").update(status="reviewed")

    @admin.action(description="Mark selected requests as spam")
    def mark_spam(self, request, queryset):
        queryset.update(status="spam", closed_at=timezone.now())

    @admin.action(description="Close selected requests")
    def mark_closed(self, request, queryset):
        queryset.update(status="closed", closed_at=timezone.now())

    def has_delete_permission(self, request, obj=None):
        return False

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, CounselingNote) and not instance.created_by_id:
                instance.created_by = request.user
            if isinstance(instance, ContactAttempt) and not instance.attempted_by_id:
                instance.attempted_by = request.user
            instance.save()
        formset.save_m2m()


@admin.register(CounselingCategory)
class CounselingCategoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ne", "code", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("name_en", "name_ne", "code")
    prepopulated_fields = {"code": ("name_en",)}
