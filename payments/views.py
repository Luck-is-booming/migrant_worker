from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Membership
from .forms import ManualPaymentForm
from .models import ManualPayment


def get_membership_amount(membership):
    if membership.membership_type == "life":
        return Decimal("5000.00")  # change this amount
    return Decimal("1000.00")      # change this amount


def manual_payment_view(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)
    amount = get_membership_amount(membership)

    if request.method == "POST":
        form = ManualPaymentForm(request.POST, request.FILES)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.membership = membership
            payment.amount = amount
            payment.save()

            membership.payment_status = "pending"
            membership.amount = amount
            membership.transaction_id = payment.transaction_id
            membership.save(update_fields=[
                "payment_status",
                "amount",
                "transaction_id",
            ])

            messages.success(
                request,
                "Payment proof submitted successfully. Please wait for admin approval."
            )

            return redirect("payments:payment_pending", payment_id=payment.id)

    else:
        form = ManualPaymentForm()

    return render(request, "payments/manual_payment.html", {
        "form": form,
        "membership": membership,
        "amount": amount,
    })


def payment_pending_view(request, payment_id):
    payment = get_object_or_404(ManualPayment, id=payment_id)

    return render(request, "payments/payment_pending.html", {
        "payment": payment,
    })