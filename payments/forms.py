from django import forms

from .models import ManualPayment


class ManualPaymentForm(forms.ModelForm):
    class Meta:
        model = ManualPayment
        fields = ["transaction_id", "screenshot", "note"]

        widgets = {
            "transaction_id": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter transaction/reference ID if available",
            }),
            "screenshot": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Any additional note",
            }),
        }