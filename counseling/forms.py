import time

from django import forms
from django.conf import settings
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import CounselingRequest
from .validators import normalize_international_phone


FIELD_CLASS = "form-control"


class CounselingRequestForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput, label="")
    form_started = forms.CharField(widget=forms.HiddenInput, required=True)

    class Meta:
        model = CounselingRequest
        fields = [
            "full_name",
            "phone",
            "email",
            "preferred_language",
            "location",
            "category",
            "message",
            "preferred_contact_method",
            "availability",
            "attachment",
            "consent_to_contact",
        ]
        labels = {
            "full_name": _("Full name"),
            "phone": _("Phone number"),
            "email": _("Email address (optional)"),
            "preferred_language": _("Preferred language"),
            "location": _("Municipality or current location"),
            "category": _("What is your question or problem about?"),
            "message": _("Tell us what happened or what you need help with"),
            "preferred_contact_method": _("How should we contact you?"),
            "availability": _("Best time to contact you (optional)"),
            "attachment": _("Supporting file (optional)"),
            "consent_to_contact": _("I agree that MRN Ilam may contact me about this request."),
        }
        widgets = {
            "message": forms.Textarea(attrs={"rows": 7}),
            "availability": forms.TextInput(attrs={"placeholder": _("Example: weekdays after 5 PM")}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "inputmode": "email"}),
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
        }
        help_texts = {
            "phone": _("Use a complete phone number. International formats such as +977, +91, +971, +974, +966, and +60 are accepted."),
            "message": _("Do not include passwords, OTPs, bank PINs, or full passport or citizenship details."),
            "attachment": _("PDF, JPG, PNG, or WebP only, up to 5 MB. Upload a file only when it helps explain your concern."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["form_started"] = signing.dumps(time.time(), salt="counseling-form")
        if not getattr(settings, "COUNSELING_ATTACHMENTS_ENABLED", True):
            self.fields.pop("attachment", None)

        for name, field in self.fields.items():
            if name in {"website", "form_started", "consent_to_contact"}:
                continue
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {FIELD_CLASS}".strip()
            described_by = []
            if field.help_text:
                described_by.append(f"id_{name}-help")
            if name in self.errors:
                described_by.append(f"id_{name}-errors")
                field.widget.attrs["aria-invalid"] = "true"
            if described_by:
                field.widget.attrs["aria-describedby"] = " ".join(described_by)

        consent = self.fields.get("consent_to_contact")
        if consent and "consent_to_contact" in self.errors:
            consent.widget.attrs["aria-invalid"] = "true"
            consent.widget.attrs["aria-describedby"] = "id_consent_to_contact-errors"

    def clean_phone(self):
        return normalize_international_phone(self.cleaned_data["phone"])

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise ValidationError(_("Unable to submit this form."))
        return ""

    def clean_form_started(self):
        token = self.cleaned_data.get("form_started")
        try:
            started = float(signing.loads(token, salt="counseling-form", max_age=7200))
        except (signing.BadSignature, ValueError, TypeError) as exc:
            raise ValidationError(_("This form expired. Reload the page and try again.")) from exc
        if time.time() - started < 3:
            raise ValidationError(_("Please review the form before submitting."))
        return token

    def clean_consent_to_contact(self):
        consent = self.cleaned_data.get("consent_to_contact")
        if not consent:
            raise ValidationError(_("You must agree before the counseling team can contact you."))
        return consent
