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

    list_filter = [
        "status",
        "submitted_at",
        "reviewed_at",
    ]

    search_fields = [
        "membership__name",
        "membership__transaction_id",
        "transaction_id",
    ]

    readonly_fields = [
        "submitted_at",
        "reviewed_at",
        "reviewed_by",
        "screenshot_preview",
    ]

    actions = [
        "approve_payments",
        "reject_payments",
    ]

    def membership_name(self, obj):
        return obj.membership.name

    membership_name.short_description = "Membership"

    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 300px; border-radius: 8px;" />'
                '</a>',
                obj.screenshot.url,
                obj.screenshot.url,
            )
        return "No screenshot uploaded"

    screenshot_preview.short_description = "Screenshot Preview"

    def approve_payments(self, request, queryset):
        for payment in queryset:
            payment.approve(user=request.user)

        self.message_user(request, "Selected payments approved successfully.")

    approve_payments.short_description = "Approve selected payments"

    def reject_payments(self, request, queryset):
        for payment in queryset:
            payment.reject(user=request.user)

        self.message_user(request, "Selected payments rejected.")

    reject_payments.short_description = "Reject selected payments"