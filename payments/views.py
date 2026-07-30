from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.models import Membership
from core.notifications import notify_payment_submitted

from .forms import ManualPaymentForm
from .models import ManualPayment
from .tokens import (
    make_membership_token,
    make_payment_token,
    read_membership_token,
    read_payment_token,
)


def get_membership_amount(membership):
    setting_name = (
        "LIFE_MEMBER_AMOUNT"
        if membership.membership_type == "life"
        else "GENERAL_MEMBER_AMOUNT"
    )
    raw_amount = settings.MANUAL_PAYMENT_CONFIG.get(setting_name)

    try:
        return Decimal(str(raw_amount)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ImproperlyConfigured(
            f"MANUAL_PAYMENT_CONFIG[{setting_name!r}] must be a valid number."
        ) from exc


def manual_payment_view(request, token):
    membership_id = read_membership_token(token)
    membership = get_object_or_404(Membership, id=membership_id)

    existing_payment = membership.manual_payments.exclude(
        status=ManualPayment.STATUS_REJECTED
    ).order_by("-submitted_at").first()

    if existing_payment:
        return redirect(
            "payments:payment_pending",
            token=make_payment_token(existing_payment.id),
        )

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

            payment_token = make_payment_token(payment.id)
            pending_path = reverse(
                "payments:payment_pending",
                kwargs={"token": payment_token},
            )
            pending_url = request.build_absolute_uri(pending_path)
            notify_payment_submitted(payment, pending_url)

            messages.success(
                request,
                "Payment proof submitted successfully. Please wait for admin approval.",
            )

            return redirect("payments:payment_pending", token=payment_token)
    else:
        form = ManualPaymentForm()

    return render(request, "payments/manual_payment.html", {
        "form": form,
        "membership": membership,
        "amount": amount,
    })


def payment_pending_view(request, token):
    payment_id = read_payment_token(token)
    payment = get_object_or_404(
        ManualPayment.objects.select_related("membership"),
        id=payment_id,
    )

    return render(request, "payments/payment_pending.html", {
        "payment": payment,
        "membership_token": make_membership_token(payment.membership_id),
    })
