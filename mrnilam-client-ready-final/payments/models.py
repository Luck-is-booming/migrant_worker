import logging
import re
import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.storage import get_private_media_storage




def private_payment_evidence_path(instance, filename):
    suffix = Path(filename).suffix.casefold()[:10]
    return f"private/payment_proofs/{uuid.uuid4().hex}{suffix}"


logger = logging.getLogger(__name__)


REGISTRY_BY_MUNICIPALITY = {
    "ilam": ("municipality", "Ilam Municipality"),
    "deumai": ("municipality", "Deumai Municipality"),
    "suryodaya": ("municipality", "Suryodaya Municipality"),
    "phakphokthum": ("rural_municipality", "Phakphokthum Rural Municipality"),
    "sandakpur": ("rural_municipality", "Sandakpur Rural Municipality"),
}


def get_member_registry(municipality_code):
    return REGISTRY_BY_MUNICIPALITY.get(
        municipality_code,
        ("unknown", str(municipality_code or "").strip() or "Unknown Unit"),
    )


def normalize_transaction_reference(value):
    text = str(value or "").strip().casefold()
    return re.sub(r"[\s-]+", "", text)


class ManualPayment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_NEEDS_REVIEW = "needs_review"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, _("Pending")),
        (STATUS_NEEDS_REVIEW, _("Needs review")),
        (STATUS_APPROVED, _("Approved")),
        (STATUS_REJECTED, _("Rejected")),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    membership = models.ForeignKey(
        "core.Membership",
        on_delete=models.PROTECT,
        related_name="manual_payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(
        max_length=100, blank=True, verbose_name=_("Transaction / Reference ID")
    )
    transaction_id_normalized = models.CharField(
        max_length=120, blank=True, editable=False, db_index=True
    )
    screenshot = models.ImageField(
        upload_to=private_payment_evidence_path,
        storage=get_private_media_storage,
        verbose_name=_("Payment Screenshot"),
    )
    note = models.TextField(blank=True, max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_manual_payments",
    )
    admin_note = models.TextField(
        blank=True,
        max_length=2000,
        help_text=_("Internal staff note. This is not shown to the applicant."),
    )
    rejection_reason = models.TextField(
        blank=True,
        max_length=1000,
        verbose_name=_("Applicant-facing rejection reason"),
        help_text=_("Required before rejection. Write a clear reason safe to show to the applicant."),
    )

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [models.Index(fields=["status", "-submitted_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["membership"],
                condition=Q(status__in=["pending", "needs_review", "approved"]),
                name="one_open_or_approved_payment_per_application",
            ),
            models.UniqueConstraint(
                fields=["transaction_id_normalized"],
                condition=~Q(transaction_id_normalized=""),
                name="unique_nonblank_payment_transaction_reference",
            ),
        ]

    def save(self, *args, **kwargs):
        self.transaction_id = str(self.transaction_id or "").strip()
        self.transaction_id_normalized = normalize_transaction_reference(self.transaction_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.membership.name} - Rs. {self.amount} - {self.status}"

    @staticmethod
    def _member_address(membership, unit_name):
        address = (membership.address or "").strip() or unit_name
        ward = membership.ward_no
        if ward and str(ward) not in address:
            address = f"{address} - Ward {ward}"
        return address

    def _create_or_update_member(self):
        from members.models import Member, MembershipRecord
        from members.name_utils import romanize_nepali_name
        from members.services import (
            get_or_create_category,
            get_or_create_unit,
            resolve_person_identity,
        )

        application = self.membership
        existing = MembershipRecord.objects.select_related("person").filter(
            source_application=application
        ).first()
        if existing:
            legacy = existing.legacy_member
            return legacy, existing

        level, unit_name = get_member_registry(application.municipality)
        category = get_or_create_category(application.membership_type)
        unit = get_or_create_unit(level, unit_name)
        address = self._member_address(application, unit_name)
        resolution = resolve_person_identity(
            name_ne=application.name,
            name_en=application.name_en or romanize_nepali_name(application.name),
            phone=application.phone,
            location=address,
        )
        record = MembershipRecord(
            person=resolution.person,
            category=category,
            organization_unit=unit,
            membership_number="",
            status="active",
            joined_date=application.joined_date,
            designation=application.designation,
            destination_country=application.destination_country,
            address_display=address,
            is_public=True,
            source_application=application,
        )
        # MembershipRecord.save() allocates a concurrency-safe permanent number.
        record.save()

        legacy, _ = Member.objects.update_or_create(
            source_membership=application,
            defaults={
                "name_ne": application.name,
                "name_en": application.name_en or romanize_nepali_name(application.name),
                "membership_number": record.membership_number,
                "membership_type": application.membership_type,
                "status": "active",
                "level": level,
                "unit_name": unit_name,
                "municipality": unit_name,
                "address": address,
                "designation": application.designation,
                "destination_country": application.destination_country,
                "phone": application.phone,
                "show_phone_publicly": False,
                "is_public": True,
            },
        )
        if record.legacy_member_id != legacy.pk:
            record.legacy_member = legacy
            record.save(update_fields=["legacy_member", "updated_at"])
        return legacy, record

    def _record_event(self, *, old_status, new_status, user=None, note=""):
        PaymentReviewEvent.objects.create(
            payment=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            note=note,
        )
        logger.info(
            "Payment review changed reference=%s old_status=%s new_status=%s reviewer_id=%s",
            self.public_id,
            old_status,
            new_status,
            getattr(user, "pk", None),
        )

    def approve(self, user=None):
        from core.notifications import notify_payment_reviewed

        with transaction.atomic():
            payment = type(self).objects.select_for_update().select_related("membership").get(pk=self.pk)
            old_status = payment.status
            was_approved = old_status == self.STATUS_APPROVED
            if not was_approved:
                payment.status = self.STATUS_APPROVED
                payment.reviewed_at = timezone.now()
                payment.reviewed_by = user
                payment.save(update_fields=["status", "reviewed_at", "reviewed_by"])
                payment._record_event(
                    old_status=old_status,
                    new_status=payment.status,
                    user=user,
                    note=payment.admin_note,
                )

            membership = payment.membership
            membership.payment_status = "completed"
            membership.is_approved = True
            membership.amount = payment.amount
            if payment.transaction_id:
                membership.transaction_id = payment.transaction_id
            membership.save(update_fields=["payment_status", "is_approved", "amount", "transaction_id"])
            payment._create_or_update_member()
            if not was_approved:
                notify_payment_reviewed(payment)

            self.status = payment.status
            self.reviewed_at = payment.reviewed_at
            self.reviewed_by = payment.reviewed_by

    def mark_needs_review(self, user=None, note=""):
        with transaction.atomic():
            payment = type(self).objects.select_for_update().get(pk=self.pk)
            if payment.status != self.STATUS_PENDING:
                return
            old_status = payment.status
            payment.status = self.STATUS_NEEDS_REVIEW
            payment.reviewed_at = timezone.now()
            payment.reviewed_by = user
            if note:
                payment.admin_note = note
            payment.save(
                update_fields=[
                    "status", "reviewed_at", "reviewed_by", "admin_note"
                ]
            )
            payment._record_event(
                old_status=old_status,
                new_status=payment.status,
                user=user,
                note=note or payment.admin_note,
            )
            self.status = payment.status
            self.reviewed_at = payment.reviewed_at
            self.reviewed_by = payment.reviewed_by

    def reject(self, user=None):
        from core.notifications import notify_payment_reviewed

        with transaction.atomic():
            payment = type(self).objects.select_for_update().select_related("membership").get(pk=self.pk)
            if payment.status in {self.STATUS_APPROVED, self.STATUS_REJECTED}:
                return
            if not str(payment.rejection_reason or "").strip():
                raise ValidationError(
                    _(
                        "Enter an applicant-facing rejection reason before rejecting payment."
                    )
                )
            old_status = payment.status
            payment.status = self.STATUS_REJECTED
            payment.reviewed_at = timezone.now()
            payment.reviewed_by = user
            payment.save(update_fields=["status", "reviewed_at", "reviewed_by"])
            payment._record_event(
                old_status=old_status,
                new_status=payment.status,
                user=user,
                note=payment.rejection_reason,
            )

            membership = payment.membership
            membership.payment_status = "rejected"
            membership.is_approved = False
            membership.save(update_fields=["payment_status", "is_approved"])
            notify_payment_reviewed(payment)

            self.status = payment.status
            self.reviewed_at = payment.reviewed_at
            self.reviewed_by = payment.reviewed_by


class PaymentReviewEvent(models.Model):
    payment = models.ForeignKey(ManualPayment, on_delete=models.PROTECT, related_name="review_events")
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True, max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.payment.public_id}: {self.old_status} → {self.new_status}"
