from django.core import signing
from django.http import Http404

MEMBERSHIP_SALT = "mrn-membership-payment"
PAYMENT_SALT = "mrn-payment-status"


def make_membership_token(membership_id: int) -> str:
    return signing.dumps({"membership_id": membership_id}, salt=MEMBERSHIP_SALT, compress=True)


def read_membership_token(token: str) -> int:
    try:
        payload = signing.loads(token, salt=MEMBERSHIP_SALT)
        return int(payload["membership_id"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise Http404("Invalid membership payment link.") from exc


def make_payment_token(payment_id: int) -> str:
    return signing.dumps({"payment_id": payment_id}, salt=PAYMENT_SALT, compress=True)


def read_payment_token(token: str) -> int:
    try:
        payload = signing.loads(token, salt=PAYMENT_SALT)
        return int(payload["payment_id"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise Http404("Invalid payment status link.") from exc
