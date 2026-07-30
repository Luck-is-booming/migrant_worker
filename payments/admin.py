from django.contrib import admin
from django.utils.html import format_html

from .models import ManualPayment


@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "membership_name",
        "amount",
        "status",
        "transaction_id",
        "submitted_at",
        "reviewed_at",
    ]
    list_filter = ["status", "submitted_at", "reviewed_at"]
    search_fields = [
        "membership__name",
        "membership__name_en",
        "membership__email",
        "membership__phone",
        "membership__transaction_id",
        "transaction_id",
    ]
    readonly_fields = [
        "membership",
        "amount",
        "transaction_id",
        "note",
        "submitted_at",
        "reviewed_at",
        "reviewed_by",
        "screenshot_preview",
    ]
    fields = [
        "membership",
        "amount",
        "transaction_id",
        "note",
        "status",
        "admin_note",
        "submitted_at",
        "reviewed_at",
        "reviewed_by",
        "screenshot_preview",
    ]
    actions = ["approve_payments", "reject_payments"]

    @admin.display(description="Membership")
    def membership_name(self, obj):
        return obj.membership.name

    @admin.display(description="Screenshot Preview")
    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">'
                '<img src="{}" style="max-width: 300px; border-radius: 8px;" />'
                "</a>",
                obj.screenshot.url,
                obj.screenshot.url,
            )
        return "No screenshot uploaded"

    @admin.action(description="Approve selected payments")
    def approve_payments(self, request, queryset):
        approved = 0
        for payment in queryset:
            payment.approve(user=request.user)
            approved += 1
        self.message_user(request, f"Approved {approved} payment(s).")

    @admin.action(description="Reject selected pending payments")
    def reject_payments(self, request, queryset):
        rejected = 0
        skipped = 0
        for payment in queryset:
            if payment.status == ManualPayment.STATUS_APPROVED:
                skipped += 1
                continue
            payment.reject(user=request.user)
            rejected += 1
        self.message_user(
            request,
            f"Rejected {rejected} payment(s); skipped {skipped} already approved payment(s).",
        )
