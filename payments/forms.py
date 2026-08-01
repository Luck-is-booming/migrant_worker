from django import forms
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

from .models import ManualPayment


class ManualPaymentForm(forms.ModelForm):
    MAX_SCREENSHOT_SIZE = 5 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

    class Meta:
        model = ManualPayment
        fields = ["transaction_id", "screenshot", "note"]
        widgets = {
<<<<<<< HEAD
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
=======
            "transaction_id": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "screenshot": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/jpeg,image/png,image/webp"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
>>>>>>> 1d670fd (refactor)
        }

    def clean_screenshot(self):
        screenshot = self.cleaned_data["screenshot"]
<<<<<<< HEAD

        if screenshot.size > self.MAX_SCREENSHOT_SIZE:
            raise forms.ValidationError("The screenshot must be 5 MB or smaller.")

        content_type = getattr(screenshot, "content_type", "")
        if content_type and content_type not in self.ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError("Upload a JPG, PNG, or WebP image.")

=======
        if screenshot.size > self.MAX_SCREENSHOT_SIZE:
            raise ValidationError("The screenshot must be 5 MB or smaller.")
        content_type = getattr(screenshot, "content_type", "")
        if content_type and content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValidationError("Upload a JPG, PNG, or WebP image.")
        try:
            position = screenshot.tell()
            image = Image.open(screenshot)
            image.verify()
            screenshot.seek(position)
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ValidationError("The uploaded screenshot is not a valid image.") from exc
>>>>>>> 1d670fd (refactor)
        return screenshot
