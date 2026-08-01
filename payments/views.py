from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from core.models import Membership
from core.notifications import notify_payment_submitted

from .forms import ManualPaymentForm
from .models import ManualPayment
from .tokens import make_payment_token, read_membership_token, read_payment_token


def get_membership_amount(membership):
    setting_name = (
        "LIFE_MEMBER_AMOUNT"
        if membership.membership_type == "life"
        else "GENERAL_MEMBER_AMOUNT"
    )
    raw_amount = settings.MANUAL_PAYMENT_CONFIG.get(setting_name)
    try:
        amount = Decimal(str(raw_amount)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ImproperlyConfigured(
            f"MANUAL_PAYMENT_CONFIG[{setting_name!r}] must be a valid number."
        ) from exc
    if amount <= 0:
        raise ImproperlyConfigured(
            f"MANUAL_PAYMENT_CONFIG[{setting_name!r}] must be greater than zero."
        )
    return amount


def _current_payment(membership):
    return (
        membership.manual_payments.exclude(status=ManualPayment.STATUS_REJECTED)
        .order_by("-submitted_at")
        .first()
    )


@never_cache
def manual_payment_view(request, token):
    membership_id = read_membership_token(token)
    membership = get_object_or_404(Membership, id=membership_id)

    existing_payment = _current_payment(membership)
    if existing_payment:
        return redirect(
            "payments:payment_pending",
            token=make_payment_token(existing_payment.id),
        )

    amount = get_membership_amount(membership)
    if request.method == "POST":
        form = ManualPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    locked_membership = Membership.objects.select_for_update().get(
                        pk=membership.pk
                    )
                    existing_payment = _current_payment(locked_membership)
                    if existing_payment:
                        payment = existing_payment
                    else:
                        payment = form.save(commit=False)
                        payment.membership = locked_membership
                        payment.amount = amount
                        payment.save()
                        locked_membership.payment_status = "pending"
                        locked_membership.amount = amount
                        locked_membership.transaction_id = payment.transaction_id
                        locked_membership.save(
                            update_fields=[
                                "payment_status",
                                "amount",
                                "transaction_id",
                            ]
                        )
            except IntegrityError:
                payment = _current_payment(membership)
                if payment is None:
                    raise

            payment_token = make_payment_token(payment.id)
            pending_path = reverse(
                "payments:payment_pending", kwargs={"token": payment_token}
            )
            notify_payment_submitted(
                payment, request.build_absolute_uri(pending_path)
            )
            messages.success(
                request,
                "Payment proof was received for membership verification.",
            )
            return redirect("payments:payment_pending", token=payment_token)
    else:
        form = ManualPaymentForm()

    return render(
        request,
        "payments/manual_payment.html",
        {
            "form": form,
            "membership": membership,
            "amount": amount,
            "payment_purpose": getattr(
                settings,
                "MEMBERSHIP_PAYMENT_PURPOSE",
                "Membership fee verification",
            ),
        },
    )


@never_cache
def payment_pending_view(request, token):
    payment_id = read_payment_token(token)
    payment = get_object_or_404(
        ManualPayment.objects.select_related("membership"), id=payment_id
    )
    return render(
        request,
        "payments/payment_pending.html",
        {"payment": payment},
    )
