from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html


STATUS_TONES = {
    "new": "info",
    "reviewed": "info",
    "contact_attempted": "warning",
    "in_counseling": "warning",
    "referred": "info",
    "resolved": "success",
    "closed": "neutral",
    "spam": "danger",
    "pending": "warning",
    "needs_review": "warning",
    "approved": "success",
    "completed": "success",
    "active": "success",
    "published": "success",
    "draft": "warning",
    "inactive": "neutral",
    "archived": "neutral",
    "expired": "neutral",
    "suspended": "danger",
    "rejected": "danger",
    "different": "neutral",
    "same": "success",
    "dismissed": "neutral",
}


def status_badge(value, label=None):
    """Return a consistent, accessible status badge for Django Admin."""

    normalized = str(value or "").strip().casefold()
    tone = STATUS_TONES.get(normalized, "neutral")
    text = label or value or 'Unknown'
    return format_html(
        '<span class="mrn-status-badge mrn-status--{}">{}</span>', tone, text
    )


def admin_change_link(obj, label=None):
    """Link to an object's admin change page without exposing implementation details."""

    if not obj or not getattr(obj, "pk", None):
        return "—"
    try:
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.pk],
        )
    except NoReverseMatch:
        return str(label or obj)
    return format_html('<a href="{}">{}</a>', url, label or str(obj))


class SuperuserOnlyAdminMixin:
    """Keep internal models out of the normal staff workspace."""

    def has_module_permission(self, request):
        return bool(request.user.is_active and request.user.is_superuser)

    def has_view_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser)

    def has_add_permission(self, request):
        return bool(request.user.is_active and request.user.is_superuser) and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_active and request.user.is_superuser) and super().has_delete_permission(request, obj)


class SuperuserReadOnlyAdminMixin(SuperuserOnlyAdminMixin):
    """Superuser-only audit screen with no add, edit, or delete actions."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
