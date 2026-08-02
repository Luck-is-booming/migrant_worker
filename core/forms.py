import time

from django import forms
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from counseling.validators import normalize_international_phone

from .models import ContactMessage, Membership


FIELD_CLASS = "form-control"


def prepare_accessible_fields(form, excluded=()):
    """Apply consistent classes and accessible help/error relationships."""
    for name, field in form.fields.items():
        if name in excluded:
            continue
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} {FIELD_CLASS}".strip()
        described_by = []
        if field.help_text:
            described_by.append(f"id_{name}-help")
        if name in form.errors:
            described_by.append(f"id_{name}-errors")
            field.widget.attrs["aria-invalid"] = "true"
        if described_by:
            field.widget.attrs["aria-describedby"] = " ".join(described_by)


class MembershipForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput, label="")
    form_started = forms.CharField(required=True, widget=forms.HiddenInput)
    consent_to_privacy = forms.BooleanField(
        required=True,
        label=_("I consent to the use of my details for this membership application."),
    )

    class Meta:
        model = Membership
        fields = [
            "name",
            "name_en",
            "email",
            "municipality",
            "ward_no",
            "address",
            "designation",
            "destination_country",
            "phone",
            "membership_type",
            "consent_to_privacy",
        ]
        labels = {
            "name": _("Full name"),
            "name_en": _("Name in English (optional)"),
            "email": _("Email address (optional)"),
            "municipality": _("Municipality or rural municipality"),
            "ward_no": _("Ward number"),
            "address": _("Address or locality"),
            "designation": _("Role in the organization (optional)"),
            "destination_country": _("Country of foreign employment (optional)"),
            "phone": _("Phone number"),
            "membership_type": _("Membership type"),
            "consent_to_privacy": _("Privacy consent"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "inputmode": "email"}),
            "ward_no": forms.NumberInput(attrs={"inputmode": "numeric", "min": "1"}),
        }
        help_texts = {
            "name_en": _("Leave this blank if you do not use an English spelling."),
            "phone": _("Enter a phone number that the organization can use to contact you."),
            "address": _("Enter a general locality only. Do not enter a private street address unless necessary."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["form_started"] = signing.dumps(time.time(), salt="membership-form")
        prepare_accessible_fields(
            self,
            excluded={"website", "form_started", "consent_to_privacy"},
        )
        consent = self.fields.get("consent_to_privacy")
        if consent:
            if "consent_to_privacy" in self.errors:
                consent.widget.attrs["aria-invalid"] = "true"
                consent.widget.attrs["aria-describedby"] = "id_consent_to_privacy-errors"

    def clean_phone(self):
        return normalize_international_phone(self.cleaned_data["phone"])

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise ValidationError(_("Unable to submit this form."))
        return ""

    def clean_form_started(self):
        token = self.cleaned_data.get("form_started")
        try:
            started = float(signing.loads(token, salt="membership-form", max_age=7200))
        except (signing.BadSignature, TypeError, ValueError) as exc:
            raise ValidationError(_("This form expired. Reload the page and try again.")) from exc
        if time.time() - started < 3:
            raise ValidationError(_("Please review the form before submitting."))
        return token

    def clean_consent_to_privacy(self):
        value = self.cleaned_data.get("consent_to_privacy")
        if not value:
            raise ValidationError(_("You must consent before submitting the membership application."))
        return value


class ContactMessageForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput, label="")
    form_started = forms.CharField(required=True, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = [
            "name",
            "phone",
            "email",
            "preferred_language",
            "subject",
            "message",
            "consent_to_contact",
        ]
        labels = {
            "name": _("Full name"),
            "phone": _("Phone number"),
            "email": _("Email address (optional)"),
            "preferred_language": _("Preferred language"),
            "subject": _("What is your message about?"),
            "message": _("Your message"),
            "consent_to_contact": _("I agree that MRN Ilam may contact me about this message."),
        }
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "inputmode": "email"}),
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
        }
        help_texts = {
            "phone": _("Enter a phone number that the organization can use to contact you."),
            "message": _("Do not include passwords, OTPs, bank PINs, or full identity-document details."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["form_started"] = signing.dumps(time.time(), salt="contact-form")
        prepare_accessible_fields(
            self,
            excluded={"website", "form_started", "consent_to_contact"},
        )
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
            started = float(signing.loads(token, salt="contact-form", max_age=7200))
        except (signing.BadSignature, TypeError, ValueError) as exc:
            raise ValidationError(_("This form expired. Reload the page and try again.")) from exc
        if time.time() - started < 3:
            raise ValidationError(_("Please review the form before submitting."))
        return token

    def clean_consent_to_contact(self):
        value = self.cleaned_data.get("consent_to_contact")
        if not value:
            raise ValidationError(_("You must agree before the team can contact you."))
        return value
