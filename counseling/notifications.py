import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

logger = logging.getLogger(__name__)


def notify_staff_new_request(counseling_request):
    if not settings.EMAIL_NOTIFICATIONS_ENABLED or not settings.ADMIN_NOTIFICATION_EMAIL:
        return

    def send():
        try:
            send_mail(
                subject="New counseling request received",
                message=(
                    "A new private counseling request has been saved. "
                    f"Reference: {counseling_request.public_id}. "
                    "Sign in to Django admin to review it. The message and phone "
                    "number are intentionally not included in this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
                fail_silently=False,
            )
        except Exception:
            logger.exception("Counseling notification email failed for request %s", counseling_request.public_id)

    transaction.on_commit(send)
