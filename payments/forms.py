from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError

from .models import ManualPayment, normalize_transaction_reference


class ManualPaymentForm(forms.ModelForm):
    MAX_SCREENSHOT_SIZE = 5 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

    class Meta:
        model = ManualPayment
        fields = ["transaction_id", "screenshot", "note"]
        labels = {
            "transaction_id": _("Transaction or reference number (optional)"),
            "screenshot": _("Payment receipt or screenshot"),
            "note": _("Note for the reviewer (optional)"),
        }
        help_texts = {
            "transaction_id": _("Enter the reference shown on the successful payment receipt, when available."),
            "screenshot": _("Upload a clear JPG, PNG, or WebP image up to 5 MB."),
            "note": _("Add only information that helps staff verify the payment."),
        }
        widgets = {
            "transaction_id": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "screenshot": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/jpeg,image/png,image/webp"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            described_by = []
            if field.help_text:
                described_by.append(f"id_{name}-help")
            if name in self.errors:
                described_by.append(f"id_{name}-errors")
                field.widget.attrs["aria-invalid"] = "true"
            if described_by:
                field.widget.attrs["aria-describedby"] = " ".join(described_by)

    def clean_transaction_id(self):
        value = str(self.cleaned_data.get("transaction_id") or "").strip()
        normalized = normalize_transaction_reference(value)
        if normalized and ManualPayment.objects.filter(
            transaction_id_normalized=normalized
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError(
                _("This transaction reference has already been submitted. Contact the organization if you believe this is a mistake.")
            )
        return value

    def clean_screenshot(self):
        screenshot = self.cleaned_data["screenshot"]
        if screenshot.size > self.MAX_SCREENSHOT_SIZE:
            raise ValidationError(_("The screenshot must be 5 MB or smaller."))
        content_type = getattr(screenshot, "content_type", "")
        if content_type and content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValidationError(_("Upload a JPG, PNG, or WebP image."))
        try:
            position = screenshot.tell()
            image = Image.open(screenshot)
            image.verify()
            screenshot.seek(position)
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ValidationError(_("The uploaded screenshot is not a valid image.")) from exc
        return screenshot
