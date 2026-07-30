from django import forms

from .models import ManualPayment


class ManualPaymentForm(forms.ModelForm):
    MAX_SCREENSHOT_SIZE = 5 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

    class Meta:
        model = ManualPayment
        fields = ["transaction_id", "screenshot", "note"]

        widgets = {
            "transaction_id": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter transaction/reference ID if available",
                "autocomplete": "off",
            }),
            "screenshot": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/jpeg,image/png,image/webp",
            }),
            "note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Any additional note",
            }),
        }

    def clean_screenshot(self):
        screenshot = self.cleaned_data["screenshot"]

        if screenshot.size > self.MAX_SCREENSHOT_SIZE:
            raise forms.ValidationError("The screenshot must be 5 MB or smaller.")

        content_type = getattr(screenshot, "content_type", "")
        if content_type and content_type not in self.ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError("Upload a JPG, PNG, or WebP image.")

        return screenshot
