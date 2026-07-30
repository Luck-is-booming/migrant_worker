"""Small, failure-safe email notification helpers.

Email is intentionally kept outside models/forms so business logic stays readable.
The project has no background worker yet, so messages are sent after the current
DB transaction commits. Delivery failures are logged and never undo a valid form
submission or payment decision.
"""

import logging
from collections.abc import Iterable

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction

logger = logging.getLogger(__name__)


def _clean_recipients(recipients: Iterable[str]) -> list[str]:
    return sorted({str(email).strip() for email in recipients if str(email).strip()})


def _send_email(
    *,
    subject: str,
    body: str,
    recipients: Iterable[str],
    reply_to: Iterable[str] | None = None,
) -> None:
    recipients = _clean_recipients(recipients)
    if not settings.EMAIL_NOTIFICATIONS_ENABLED or not recipients:
        return

    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            reply_to=_clean_recipients(reply_to or []),
        )
        message.send(fail_silently=False)
    except Exception:
        logger.exception("Could not send notification email: %s", subject)


def send_after_commit(**kwargs) -> None:
    transaction.on_commit(lambda: _send_email(**kwargs))


def notify_contact_message(contact) -> None:
    send_after_commit(
        subject=f"New website message: {contact.subject}",
        body=(
            "A new message was submitted through the MRN Ilam website.\n\n"
            f"Name: {contact.name}\n"
            f"Email: {contact.email}\n"
            f"Subject: {contact.subject}\n\n"
            f"Message:\n{contact.message}\n"
        ),
        recipients=[settings.ADMIN_NOTIFICATION_EMAIL],
        reply_to=[contact.email],
    )


def notify_membership_application(membership, payment_url: str) -> None:
    admin_body = (
        "A new membership application was submitted.\n\n"
        f"Applicant: {membership.name}\n"
        f"Email: {membership.email or 'Not provided'}\n"
        f"Phone: {membership.phone or 'Not provided'}\n"
        f"Local level: {membership.get_municipality_display()}\n"
        f"Membership type: {membership.get_membership_type_display()}\n"
        f"Payment page: {payment_url}\n"
    )
    send_after_commit(
        subject=f"New membership application: {membership.name}",
        body=admin_body,
        recipients=[settings.ADMIN_NOTIFICATION_EMAIL],
    )

    if membership.email:
        send_after_commit(
            subject="MRN Ilam membership application received",
            body=(
                f"Hello {membership.name},\n\n"
                "We received your MRN Ilam membership application. "
                "Use the secure link below to complete the QR payment step:\n\n"
                f"{payment_url}\n\n"
                "Keep this link private because it opens your application payment page.\n\n"
                "MRN Ilam"
            ),
            recipients=[membership.email],
        )


def notify_payment_submitted(payment, pending_url: str) -> None:
    membership = payment.membership
    send_after_commit(
        subject=f"Payment proof submitted: {membership.name}",
        body=(
            "A membership payment proof is ready for review.\n\n"
            f"Applicant: {membership.name}\n"
            f"Membership type: {membership.get_membership_type_display()}\n"
            f"Amount: NPR {payment.amount}\n"
            f"Transaction/reference: {payment.transaction_id or 'Not provided'}\n"
            f"Submitted: {payment.submitted_at}\n"
        ),
        recipients=[settings.ADMIN_NOTIFICATION_EMAIL],
    )

    if membership.email:
        send_after_commit(
            subject="MRN Ilam payment proof received",
            body=(
                f"Hello {membership.name},\n\n"
                f"We received your payment proof for NPR {payment.amount}. "
                "It is waiting for administrator verification.\n\n"
                f"Status page: {pending_url}\n\n"
                "MRN Ilam"
            ),
            recipients=[membership.email],
        )


def notify_payment_reviewed(payment) -> None:
    membership = payment.membership
    if not membership.email:
        return

    approved = payment.status == payment.STATUS_APPROVED
    status_text = "approved" if approved else "rejected"
    extra = (
        "Your membership is now active in the official member registry."
        if approved
        else "Please contact MRN Ilam or submit a new proof after correcting the payment issue."
    )
    admin_note = f"\nAdministrator note: {payment.admin_note}\n" if payment.admin_note else ""

    send_after_commit(
        subject=f"MRN Ilam payment {status_text}",
        body=(
            f"Hello {membership.name},\n\n"
            f"Your membership payment has been {status_text}.\n"
            f"{extra}\n"
            f"{admin_note}\n"
            "MRN Ilam"
        ),
        recipients=[membership.email],
    )
