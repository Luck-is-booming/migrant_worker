import time

from django import forms
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from counseling.validators import normalize_nepal_phone

from .models import ContactMessage, Membership


FIELD_CLASS = "form-control"


class MembershipForm(forms.ModelForm):
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
        ]
<<<<<<< HEAD

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm",
                "placeholder": "Full name",
            }),
            "name_en": forms.TextInput(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm",
                "placeholder": "Name in English, optional",
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm",
                "placeholder": "Email address for status updates, optional",
                "autocomplete": "email",
            }),
            "municipality": forms.Select(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm bg-white",
            }),
            "ward_no": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm",
                "placeholder": "Ward no.",
            }),
            "address": forms.TextInput(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm",
                "placeholder": "Address",
            }),
            "designation": forms.TextInput(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm",
                "placeholder": "Designation / position, optional",
            }),
            "destination_country": forms.TextInput(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm",
                "placeholder": "Foreign employment country, optional",
            }),
            "phone": forms.TextInput(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm",
                "placeholder": "Phone number",
            }),
            "membership_type": forms.Select(attrs={
                "class": "w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm bg-white",
            }),
=======
        labels = {
            "name": _("Full name"),
            "name_en": _("Name in English (optional)"),
            "email": _("Email address (optional)"),
            "municipality": _("Municipality"),
            "ward_no": _("Ward number"),
            "address": _("General address/locality"),
            "designation": _("Organization designation (optional)"),
            "destination_country": _("Foreign-employment country (optional)"),
            "phone": _("Phone number"),
            "membership_type": _("Membership category"),
>>>>>>> 1d670fd (refactor)
        }
        widgets = {
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = FIELD_CLASS

    def clean_phone(self):
        return normalize_nepal_phone(self.cleaned_data["phone"])


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
            "subject": _("Subject"),
            "message": _("Message"),
            "consent_to_contact": _("I consent to being contacted about this message."),
        }
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }
        help_texts = {
            "message": _("Do not submit passwords, OTPs, bank PINs, or complete identity-document details."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["form_started"] = signing.dumps(time.time(), salt="contact-form")
        for name, field in self.fields.items():
            if name not in {"website", "form_started", "consent_to_contact"}:
                field.widget.attrs["class"] = FIELD_CLASS

    def clean_phone(self):
        return normalize_nepal_phone(self.cleaned_data["phone"])

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise ValidationError(_("Unable to submit this form."))
        return ""

    def clean_form_started(self):
        token = self.cleaned_data.get("form_started")
        try:
            started = float(signing.loads(token, salt="contact-form", max_age=7200))
        except (signing.BadSignature, TypeError, ValueError) as exc:
            raise ValidationError(_("This form expired. Reload and try again.")) from exc
        if time.time() - started < 3:
            raise ValidationError(_("Please review the form before submitting."))
        return token

    def clean_consent_to_contact(self):
        value = self.cleaned_data.get("consent_to_contact")
        if not value:
            raise ValidationError(_("Consent is required so the team can contact you."))
        return value
