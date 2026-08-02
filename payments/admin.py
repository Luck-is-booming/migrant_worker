import mimetypes

from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from migrantcenter.admin_helpers import admin_change_link, status_badge

from .models import ManualPayment, PaymentReviewEvent


ManualPayment._meta.verbose_name = 'Payment review'
ManualPayment._meta.verbose_name_plural = 'Payment reviews'


class PaymentReviewEventInline(admin.TabularInline):
    model = PaymentReviewEvent
    extra = 0
    can_delete = False
    fields = ("old_status", "new_status", "changed_by", "note", "created_at")
    readonly_fields = fields
    verbose_name = 'Review history entry'
    verbose_name_plural = 'Review history'


@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "membership_name",
        "amount",
        "status_badge",
        "submitted_at",
        "reviewed_at",
        "reviewed_by",
    )
    list_filter = ("status", "submitted_at", "reviewed_at")
    search_fields = (
        "public_id",
        "membership__name",
        "membership__name_en",
        "membership__phone",
        "transaction_id",
        "membership__normalized_membership__membership_number",
    )
    readonly_fields = (
        "public_id",
        "application_link",
        "amount",
        "transaction_id",
        "transaction_id_normalized",
        "note",
        "submitted_at",
        "reviewed_at",
        "reviewed_by",
        "screenshot_preview",
        "person_record_link",
        "issued_membership_link",
    )
    actions = ("approve_payments", "mark_needs_review", "reject_payments")
    inlines = (PaymentReviewEventInline,)
    list_per_page = 30
    save_on_top = True

    fieldsets = (
        (
            'Applicant and application',
            {
                "fields": ("public_id", "application_link"),
                "description": "Open the application to see the applicant's full details.",
            },
        ),
        (
            'Payment proof',
            {
                "fields": (
                    "amount",
                    "transaction_id",
                    "note",
                    "screenshot_preview",
                ),
                "description": 'Compare the amount, transaction reference, recipient and screenshot before making a decision.',
            },
        ),
        (
            'Review decision',
            {
                "fields": ("status", "rejection_reason", "admin_note"),
                "description": 'The rejection reason is shown to the applicant. The admin note remains private.',
            },
        ),
        (
            'Resulting member records',
            {"fields": ("person_record_link", "issued_membership_link")},
        ),
        (
            'Technical and audit details',
            {
                "fields": (
                    "transaction_id_normalized",
                    "submitted_at",
                    "reviewed_at",
                    "reviewed_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "membership",
            "reviewed_by",
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if not request.user.is_superuser:
            fieldsets = [
                item for item in fieldsets if item[0] != 'Technical and audit details'
            ]
        return tuple(fieldsets)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:object_id>/evidence/",
                self.admin_site.admin_view(self.evidence_view),
                name="payments_manualpayment_evidence",
            )
        ]
        return custom + urls

    def evidence_view(self, request, object_id):
        if not request.user.has_perm("payments.view_manualpayment"):
            raise Http404
        payment = get_object_or_404(ManualPayment, pk=object_id)
        if not payment.screenshot:
            raise Http404
        try:
            file_handle = payment.screenshot.open("rb")
        except (OSError, ValueError) as exc:
            raise Http404 from exc
        content_type = mimetypes.guess_type(payment.screenshot.name)[0] or "application/octet-stream"
        response = FileResponse(file_handle, content_type=content_type)
        response["Cache-Control"] = "private, no-store"
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

    @admin.display(description='Reference')
    def reference(self, obj):
        return str(obj.public_id)[:8]

    @admin.display(description='Applicant')
    def membership_name(self, obj):
        return obj.membership.name

    @admin.display(description='Status', ordering="status")
    def status_badge(self, obj):
        return status_badge(obj.status, obj.get_status_display())

    @admin.display(description='Membership application')
    def application_link(self, obj):
        if not obj or not obj.membership_id:
            return "—"
        return admin_change_link(obj.membership, 'Open membership application')

    def _issued_membership(self, obj):
        if not obj or not obj.membership_id:
            return None
        try:
            return obj.membership.normalized_membership
        except (AttributeError, ObjectDoesNotExist):
            return None

    @admin.display(description='Person record')
    def person_record_link(self, obj):
        issued = self._issued_membership(obj)
        if not issued:
            return 'A person record has not been created yet.'
        return admin_change_link(issued.person, 'Open person record')

    @admin.display(description='Issued membership')
    def issued_membership_link(self, obj):
        issued = self._issued_membership(obj)
        if not issued:
            return 'A membership has not been issued yet.'
        return admin_change_link(
            issued,
            issued.membership_number or 'Open issued membership',
        )

    @admin.display(description='Private payment screenshot')
    def screenshot_preview(self, obj):
        if not obj or not obj.pk or not obj.screenshot:
            return 'No screenshot uploaded.'
        url = reverse("admin:payments_manualpayment_evidence", args=[obj.pk])
        return format_html(
            '<p><strong>{}</strong></p>'
            '<a href="{}" target="_blank" rel="noopener noreferrer">'
            '<img class="mrn-admin-preview" src="{}" alt="{}"></a>',
            'Authorized staff only.',
            url,
            url,
            'Private payment evidence',
        )

    @admin.action(description='Approve selected pending payments')
    def approve_payments(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status != ManualPayment.STATUS_APPROVED:
                payment.approve(user=request.user)
                count += 1
        self.message_user(
            request,
            'Approved %(count)s payment(s).' % {"count": count},
            messages.SUCCESS,
        )

    @admin.action(description='Mark selected payments as needing review')
    def mark_needs_review(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status == ManualPayment.STATUS_PENDING:
                payment.mark_needs_review(user=request.user)
                count += 1
        self.message_user(
            request,
            'Marked %(count)s payment(s) for additional review.' % {"count": count},
            messages.SUCCESS,
        )

    @admin.action(description='Reject selected pending or review payments')
    def reject_payments(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status in {
                ManualPayment.STATUS_PENDING,
                ManualPayment.STATUS_NEEDS_REVIEW,
            }:
                try:
                    payment.reject(user=request.user)
                    count += 1
                except ValidationError as exc:
                    self.message_user(
                        request,
                        'Could not reject %(reference)s: %(error)s'
                        % {
                            "reference": payment.public_id,
                            "error": "; ".join(exc.messages),
                        },
                        messages.ERROR,
                    )
        if count:
            self.message_user(
                request,
                'Rejected %(count)s payment(s).' % {"count": count},
                messages.SUCCESS,
            )

    def has_delete_permission(self, request, obj=None):
        return False
