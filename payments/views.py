import json
import base64
import logging
import time
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from core.models import Membership
from .utils import generate_esewa_signature

logger = logging.getLogger(__name__)


def _membership_amount(membership):
    esewa = settings.ESEWA_CONFIG
    if membership.membership_type == "general":
        return esewa["GENERAL_MEMBER_AMOUNT"]
    return esewa["LIFE_MEMBER_AMOUNT"]


def _parse_membership_id(transaction_uuid):
    membership_id = transaction_uuid.split("-", 1)[0]
    return int(membership_id)


@require_http_methods(["GET"])
def initiate_payment(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)
    esewa = settings.ESEWA_CONFIG

    unique_transaction_uuid = f"{membership.id}-{int(time.time())}"
    amount = _membership_amount(membership)
    product_code = esewa["MERCHANT_ID"]

    signature = generate_esewa_signature(
        amount,
        unique_transaction_uuid,
        product_code,
        esewa["SECRET_KEY"],
    )

    membership.amount = Decimal(amount)
    membership.transaction_id = unique_transaction_uuid
    membership.payment_status = "pending"
    membership.save(update_fields=["amount", "transaction_id", "payment_status"])

    form_data = {
        "amount": amount,
        "tax_amount": "0",
        "total_amount": amount,
        "transaction_uuid": unique_transaction_uuid,
        "product_code": product_code,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": request.build_absolute_uri(reverse("payments:payment_success")),
        "failure_url": request.build_absolute_uri(reverse("payments:payment_failure")),
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": signature,
    }

    return render(request, "payments/initiate.html", {
        "initiate_url": esewa["INITIATE_URL"],
        "form_data": form_data,
    })


@csrf_exempt
@require_GET
def esewa_success(request):
    encoded_data = request.GET.get("data")

    if not encoded_data:
        messages.error(request, _("Payment validation failed or data was tampered with."))
        return redirect("index")

    try:
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        response_dict = json.loads(decoded_data)
        returned_uuid = response_dict.get("transaction_uuid")

        if not returned_uuid or response_dict.get("status") != "COMPLETE":
            raise ValueError("Incomplete or invalid payment status")

        membership = get_object_or_404(Membership, id=_parse_membership_id(returned_uuid))
        membership.is_approved = True
        membership.payment_status = "completed"
        membership.transaction_id = returned_uuid

        total_amount = response_dict.get("total_amount")
        if total_amount:
            membership.amount = Decimal(str(total_amount))

        membership.save(update_fields=["is_approved", "payment_status", "transaction_id", "amount"])
        messages.success(request, _("Payment successful! Your membership is active."))
        return redirect("index")

    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning("eSewa callback validation failed: %s", exc)
    except Exception:
        logger.exception("eSewa callback processing error")

    messages.error(request, _("Payment validation failed or data was tampered with."))
    return redirect("index")


@csrf_exempt
@require_GET
def esewa_failure(request):
    messages.error(request, _("Payment was cancelled. Please try submitting your form again."))
    return redirect("index")
