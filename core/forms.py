from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage, Membership


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
        }

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white',
            }),
            'message': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all bg-white',
            }),
        }
