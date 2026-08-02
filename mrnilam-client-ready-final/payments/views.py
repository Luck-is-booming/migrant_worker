from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext as _

from core.models import Membership, MembershipPaymentSettings
from core.notifications import notify_payment_submitted

from .forms import ManualPaymentForm
from .models import ManualPayment
from .tokens import make_membership_token, make_payment_token, read_membership_token, read_payment_token


def get_membership_amount(membership, payment_settings=None):
    if payment_settings and payment_settings.is_active:
        raw_amount = payment_settings.amount_for(membership.membership_type)
        setting_name = "database payment settings"
    else:
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
            f"Membership amount from {setting_name!r} must be a valid number."
        ) from exc
    if amount <= 0:
        raise ImproperlyConfigured(
            f"Membership amount from {setting_name!r} must be greater than zero."
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

    payment_settings = MembershipPaymentSettings.objects.first()
    payment_ready = bool(payment_settings and payment_settings.is_ready)
    if not payment_ready:
        return render(
            request,
            "payments/manual_payment.html",
            {
                "form": None,
                "membership": membership,
                "payment_ready": False,
                "payment_settings": payment_settings,
            },
        )

    amount = get_membership_amount(membership, payment_settings)
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
                _("Payment proof was received for membership verification."),
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
            "payment_ready": True,
            "payment_settings": payment_settings,
            "qr_url": payment_settings.payment_qr.url,
            "recipient_name": payment_settings.recipient_name,
            "account_details": payment_settings.account_details,
            "payment_instructions": payment_settings.instructions,
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
        ManualPayment.objects.select_related(
            "membership", "membership__normalized_membership",
            "membership__normalized_membership__organization_unit",
            "membership__normalized_membership__category",
        ),
        id=payment_id,
    )
    retry_url = ""
    if payment.status == ManualPayment.STATUS_REJECTED:
        retry_url = reverse(
            "payments:manual_payment",
            kwargs={"token": make_membership_token(payment.membership_id)},
        )
    return render(
        request,
        "payments/payment_pending.html",
        {
            "payment": payment,
            "retry_url": retry_url,
            "official_membership": getattr(
                payment.membership, "normalized_membership", None
            ),
        },
    )
