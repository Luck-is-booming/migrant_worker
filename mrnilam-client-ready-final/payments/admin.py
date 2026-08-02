import mimetypes

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from .models import ManualPayment, PaymentReviewEvent


class PaymentReviewEventInline(admin.TabularInline):
    model = PaymentReviewEvent
    extra = 0
    can_delete = False
    fields = ("old_status", "new_status", "changed_by", "note", "created_at")
    readonly_fields = fields


@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "membership_name", "amount", "status",
        "submitted_at", "reviewed_at", "reviewed_by",
    )
    list_filter = ("status", "submitted_at", "reviewed_at")
    search_fields = (
        "public_id", "membership__name", "membership__name_en",
        "membership__phone", "transaction_id",
    )
    readonly_fields = (
        "public_id", "membership", "amount", "transaction_id", "transaction_id_normalized", "note",
        "submitted_at", "reviewed_at", "reviewed_by", "screenshot_preview",
    )
    fields = (
        "public_id", "membership", "amount", "transaction_id", "transaction_id_normalized", "note",
        "status", "rejection_reason", "admin_note", "submitted_at", "reviewed_at", "reviewed_by",
        "screenshot_preview",
    )
    actions = ("approve_payments", "mark_needs_review", "reject_payments")
    inlines = (PaymentReviewEventInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("membership", "reviewed_by")

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

    @admin.display(description="Reference")
    def reference(self, obj):
        return str(obj.public_id)[:8]

    @admin.display(description="Membership")
    def membership_name(self, obj):
        return obj.membership.name

    @admin.display(description="Private screenshot")
    def screenshot_preview(self, obj):
        if not obj.pk or not obj.screenshot:
            return "No screenshot uploaded"
        url = reverse("admin:payments_manualpayment_evidence", args=[obj.pk])
        return format_html(
            '<p><strong>Authorized staff only.</strong> Evidence is streamed through a protected admin URL.</p>'
            '<a href="{}" target="_blank" rel="noopener noreferrer">'
            '<img src="{}" alt="Private payment evidence" style="max-width:300px;border-radius:8px"></a>',
            url, url,
        )

    @admin.action(description="Approve selected pending payments")
    def approve_payments(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status != ManualPayment.STATUS_APPROVED:
                payment.approve(user=request.user)
                count += 1
        self.message_user(request, f"Approved {count} payment(s).")

    @admin.action(description="Mark selected pending payments as needing review")
    def mark_needs_review(self, request, queryset):
        count = 0
        for payment in queryset:
            if payment.status == ManualPayment.STATUS_PENDING:
                payment.mark_needs_review(user=request.user)
                count += 1
        self.message_user(request, f"Marked {count} payment(s) for additional review.")

    @admin.action(description="Reject selected pending/review payments")
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
                        f"Could not reject {payment.public_id}: {'; '.join(exc.messages)}",
                        messages.ERROR,
                    )
        if count:
            self.message_user(request, f"Rejected {count} payment(s).", messages.SUCCESS)

    def has_delete_permission(self, request, obj=None):
        return False
