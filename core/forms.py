from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage, Membership


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['name', 'municipality', 'membership_type']

        labels = {
            'name': _('Full Name'),
            'municipality': _('Local Level'),
            'membership_type': _('Membership Type'),
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': _('Enter your name'),
            }),
            'municipality': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
            }),
            'membership_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
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
