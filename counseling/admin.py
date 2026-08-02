import mimetypes

from django.contrib import admin, messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from migrantcenter.admin_helpers import status_badge

from .models import ContactAttempt, CounselingCategory, CounselingNote, CounselingRequest


CounselingRequest._meta.verbose_name = 'Counseling request'
CounselingRequest._meta.verbose_name_plural = 'Counseling requests'


class CounselingNoteInline(admin.TabularInline):
    model = CounselingNote
    extra = 0
    can_delete = False
    fields = ("note", "created_by", "created_at")
    readonly_fields = ("created_by", "created_at")
    verbose_name = 'Internal note'
    verbose_name_plural = 'Internal notes'


class ContactAttemptInline(admin.TabularInline):
    model = ContactAttempt
    extra = 0
    can_delete = False
    fields = ("method", "outcome", "note", "attempted_by", "attempted_at")
    readonly_fields = ("attempted_by", "attempted_at")
    verbose_name = 'Contact attempt'
    verbose_name_plural = 'Contact history'


@admin.register(CounselingRequest)
class CounselingRequestAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "full_name",
        "masked_phone",
        "category",
        "status_badge",
        "assigned_to",
        "created_at",
    )
    list_filter = (
        "status",
        "category",
        "preferred_language",
        "preferred_contact_method",
        "created_at",
    )
    search_fields = ("public_id", "full_name", "phone", "email", "location", "message")
    date_hierarchy = "created_at"
    list_select_related = ("category", "assigned_to")
    autocomplete_fields = ("assigned_to",)
    readonly_fields = (
        "public_id",
        "consent_recorded_at",
        "source_ip_hash",
        "created_at",
        "updated_at",
        "attachment_preview",
    )
    inlines = (ContactAttemptInline, CounselingNoteInline)
    actions = (
        "assign_to_me",
        "mark_reviewed",
        "mark_contact_attempted",
        "mark_resolved",
        "mark_closed",
        "mark_spam",
    )
    list_per_page = 30
    save_on_top = True

    fieldsets = (
        (
            'Person and contact details',
            {
                "fields": (
                    "public_id",
                    "full_name",
                    "phone",
                    "email",
                    "location",
                    "preferred_language",
                    "preferred_contact_method",
                    "availability",
                )
            },
        ),
        (
            'Question or problem',
            {
                "fields": (
                    "category",
                    "message",
                    "attachment_preview",
                    "consent_to_contact",
                    "consent_recorded_at",
                )
            },
        ),
        (
            'Staff follow-up',
            {
                "fields": ("status", "assigned_to", "internal_summary", "closed_at"),
                "description": 'Update the status as the request moves from review to contact, counseling and closure.',
            },
        ),
        (
            'Record handling',
            {
                "fields": ("retention_status",),
                "classes": ("collapse",),
                "description": "Change this only when carrying out the organization's retention policy.",
            },
        ),
        (
            'Technical record',
            {
                "fields": ("source_ip_hash", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if not request.user.is_superuser:
            fieldsets = [item for item in fieldsets if item[0] != 'Technical record']
        return tuple(fieldsets)

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

    @admin.display(description='Private attachment')
    def attachment_preview(self, obj):
        if not obj or not obj.attachment:
            return 'No attachment was submitted.'
        url = reverse("admin:counseling_counselingrequest_attachment", args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
            url,
            'Open protected attachment',
        )

    @admin.display(description='Reference')
    def reference(self, obj):
        return str(obj.public_id)[:8]

    @admin.display(description='Phone')
    def masked_phone(self, obj):
        return f"••••••{obj.phone[-4:]}" if obj.phone else "—"

    @admin.display(description='Status', ordering="status")
    def status_badge(self, obj):
        return status_badge(obj.status, obj.get_status_display())

    @admin.action(description='Assign selected requests to me')
    def assign_to_me(self, request, queryset):
        updated = queryset.exclude(status__in=["closed", "spam"]).update(
            assigned_to=request.user
        )
        self.message_user(
            request,
            'Assigned %(count)s request(s) to you.' % {"count": updated},
            messages.SUCCESS,
        )

    @admin.action(description='Mark selected requests as reviewed')
    def mark_reviewed(self, request, queryset):
        updated = queryset.filter(status="new").update(status="reviewed")
        self.message_user(request, 'Marked %(count)s request(s) as reviewed.' % {"count": updated})

    @admin.action(description='Mark selected requests as contact attempted')
    def mark_contact_attempted(self, request, queryset):
        updated = queryset.exclude(status__in=["closed", "spam"]).update(status="contact_attempted")
        self.message_user(request, 'Updated %(count)s request(s).' % {"count": updated})

    @admin.action(description='Mark selected requests as resolved')
    def mark_resolved(self, request, queryset):
        updated = queryset.exclude(status="spam").update(status="resolved")
        self.message_user(request, 'Resolved %(count)s request(s).' % {"count": updated})

    @admin.action(description='Close selected requests')
    def mark_closed(self, request, queryset):
        updated = queryset.exclude(status="spam").update(status="closed", closed_at=timezone.now())
        self.message_user(request, 'Closed %(count)s request(s).' % {"count": updated})

    @admin.action(description='Mark selected requests as spam')
    def mark_spam(self, request, queryset):
        updated = queryset.update(status="spam", closed_at=timezone.now())
        self.message_user(request, 'Marked %(count)s request(s) as spam.' % {"count": updated})

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
