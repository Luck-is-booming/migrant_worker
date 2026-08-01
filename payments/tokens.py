from django.core import signing
from django.http import Http404

MEMBERSHIP_SALT = "mrn-membership-payment"
PAYMENT_SALT = "mrn-payment-status"
<<<<<<< HEAD
=======
MEMBERSHIP_LINK_MAX_AGE = 60 * 60 * 24 * 30
PAYMENT_LINK_MAX_AGE = 60 * 60 * 24 * 90
>>>>>>> 1d670fd (refactor)


def make_membership_token(membership_id: int) -> str:
    return signing.dumps({"membership_id": membership_id}, salt=MEMBERSHIP_SALT, compress=True)


def read_membership_token(token: str) -> int:
    try:
<<<<<<< HEAD
        payload = signing.loads(token, salt=MEMBERSHIP_SALT)
        return int(payload["membership_id"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise Http404("Invalid membership payment link.") from exc
=======
        payload = signing.loads(token, salt=MEMBERSHIP_SALT, max_age=MEMBERSHIP_LINK_MAX_AGE)
        return int(payload["membership_id"])
    except (signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError) as exc:
        raise Http404("Invalid or expired membership payment link.") from exc
>>>>>>> 1d670fd (refactor)


def make_payment_token(payment_id: int) -> str:
    return signing.dumps({"payment_id": payment_id}, salt=PAYMENT_SALT, compress=True)


def read_payment_token(token: str) -> int:
    try:
<<<<<<< HEAD
        payload = signing.loads(token, salt=PAYMENT_SALT)
        return int(payload["payment_id"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise Http404("Invalid payment status link.") from exc
=======
        payload = signing.loads(token, salt=PAYMENT_SALT, max_age=PAYMENT_LINK_MAX_AGE)
        return int(payload["payment_id"])
    except (signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, ValueError) as exc:
        raise Http404("Invalid or expired payment status link.") from exc
>>>>>>> 1d670fd (refactor)
