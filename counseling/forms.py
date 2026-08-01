import time

from django import forms
from django.conf import settings
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import CounselingRequest
from .validators import normalize_nepal_phone


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
            "location": _("Municipality or location"),
            "category": _("What do you need guidance about?"),
            "message": _("Describe your concern"),
            "preferred_contact_method": _("Preferred contact method"),
            "availability": _("When are you usually available? (optional)"),
            "attachment": _("Supporting file (optional)"),
            "consent_to_contact": _("I consent to being contacted about this request."),
        }
        widgets = {
            "message": forms.Textarea(attrs={"rows": 7}),
            "availability": forms.TextInput(attrs={"placeholder": _("Example: weekdays after 5 PM")}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
        }
        help_texts = {
            "phone": _("Accepted formats include 98XXXXXXXX and +977 98XXXXXXXX."),
            "message": _("Do not include passwords, OTPs, bank PINs, or complete passport/citizenship details."),
            "attachment": _("PDF or image only, maximum 5 MB. Upload only when it is necessary to explain the concern."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["form_started"] = signing.dumps(time.time(), salt="counseling-form")
        for name, field in self.fields.items():
            if name not in {"website", "form_started", "consent_to_contact"}:
                existing = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{existing} {FIELD_CLASS}".strip()
        if not getattr(settings, "COUNSELING_ATTACHMENTS_ENABLED", True):
            self.fields.pop("attachment", None)

    def clean_phone(self):
        return normalize_nepal_phone(self.cleaned_data["phone"])

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
            raise ValidationError(_("Consent is required so the counseling team can contact you."))
        return consent
