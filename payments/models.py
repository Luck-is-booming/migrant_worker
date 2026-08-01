import logging
import uuid
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone


<<<<<<< HEAD
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
        ("unknown", str(municipality_code or "").strip()),
=======


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
>>>>>>> 1d670fd (refactor)
    )


class ManualPayment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_NEEDS_REVIEW = "needs_review"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_NEEDS_REVIEW, "Needs review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    membership = models.ForeignKey(
        "core.Membership",
        on_delete=models.PROTECT,
        related_name="manual_payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
<<<<<<< HEAD
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Transaction / Reference ID",
    )
    screenshot = models.ImageField(
        upload_to="payment_proofs/",
        verbose_name="Payment Screenshot",
    )
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
=======
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="Transaction / Reference ID")
    screenshot = models.ImageField(upload_to=private_payment_evidence_path, verbose_name="Payment Screenshot")
    note = models.TextField(blank=True, max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
>>>>>>> 1d670fd (refactor)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_manual_payments",
    )
<<<<<<< HEAD
    admin_note = models.TextField(blank=True)
=======
    admin_note = models.TextField(blank=True, max_length=2000)
>>>>>>> 1d670fd (refactor)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [models.Index(fields=["status", "-submitted_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["membership"],
                condition=Q(status__in=["pending", "needs_review", "approved"]),
                name="one_open_or_approved_payment_per_application",
            )
        ]

    def __str__(self):
        return f"{self.membership.name} - Rs. {self.amount} - {self.status}"

    @staticmethod
    def _member_address(membership, unit_name):
<<<<<<< HEAD
        address = (membership.address or "").strip()
        ward = membership.ward_no

        if not address:
            address = unit_name

        if ward and str(ward) not in address:
            address = f"{address} - Ward {ward}"

=======
        address = (membership.address or "").strip() or unit_name
        ward = membership.ward_no
        if ward and str(ward) not in address:
            address = f"{address} - Ward {ward}"
>>>>>>> 1d670fd (refactor)
        return address

    def _create_or_update_member(self):
        Member = apps.get_model("members", "Member")
        from members.name_utils import romanize_nepali_name
<<<<<<< HEAD

        membership = self.membership
        level, unit_name = get_member_registry(membership.municipality)

        member = Member.objects.filter(source_membership=membership).first()

        # Attach records produced by the older MWRWPC-0001 numbering logic,
        # instead of creating a duplicate after this upgrade.
=======
        from members.services import sync_legacy_member

        membership = self.membership
        level, unit_name = get_member_registry(membership.municipality)
        member = Member.objects.filter(source_membership=membership).first()

>>>>>>> 1d670fd (refactor)
        if member is None:
            legacy_number = f"MWRWPC-{membership.id:04d}"
            member = Member.objects.filter(
                membership_number=legacy_number,
                source_membership__isnull=True,
            ).first()
            if member is not None:
                member.source_membership = membership
                member.membership_number = ""
                member.membership_number_int = None

        if member is None:
            member = Member(source_membership=membership)

        registry_changed = member.pk and (
            member.level != level
            or member.unit_name != unit_name
            or member.membership_type != membership.membership_type
        )
        if registry_changed:
            member.membership_number = ""
            member.membership_number_int = None

        member.name_ne = membership.name
        member.name_en = membership.name_en or romanize_nepali_name(membership.name)
        member.membership_type = membership.membership_type
        member.status = "active"
        member.level = level
        member.unit_name = unit_name
        member.municipality = unit_name
        member.address = self._member_address(membership, unit_name)
        member.designation = membership.designation
        member.destination_country = membership.destination_country
        member.phone = membership.phone
        member.show_phone_publicly = False
        member.is_public = True
        member.save()
<<<<<<< HEAD

        return member
=======
        normalized = sync_legacy_member(member)
        return member, normalized

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
>>>>>>> 1d670fd (refactor)

    def approve(self, user=None):
        from core.notifications import notify_payment_reviewed

        with transaction.atomic():
<<<<<<< HEAD
            payment = type(self).objects.select_for_update().select_related(
                "membership"
            ).get(pk=self.pk)

            was_approved = payment.status == self.STATUS_APPROVED
            if not was_approved:
                payment.status = self.STATUS_APPROVED
                payment.reviewed_at = timezone.now()
                payment.reviewed_by = user
                payment.save(update_fields=["status", "reviewed_at", "reviewed_by"])

            membership = payment.membership
            membership.payment_status = "completed"
            membership.is_approved = True
            membership.amount = payment.amount
            if payment.transaction_id:
                membership.transaction_id = payment.transaction_id
            membership.save(update_fields=[
                "payment_status",
                "is_approved",
                "amount",
                "transaction_id",
            ])

            payment._create_or_update_member()
            if not was_approved:
                notify_payment_reviewed(payment)

=======
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
>>>>>>> 1d670fd (refactor)
            self.status = payment.status
            self.reviewed_at = payment.reviewed_at
            self.reviewed_by = payment.reviewed_by

    def reject(self, user=None):
        from core.notifications import notify_payment_reviewed

        with transaction.atomic():
<<<<<<< HEAD
            payment = type(self).objects.select_for_update().select_related(
                "membership"
            ).get(pk=self.pk)

            # Do not accidentally undo an already approved membership or
            # resend rejection notifications for an unchanged decision.
            if payment.status in {self.STATUS_APPROVED, self.STATUS_REJECTED}:
                return

=======
            payment = type(self).objects.select_for_update().select_related("membership").get(pk=self.pk)
            if payment.status in {self.STATUS_APPROVED, self.STATUS_REJECTED}:
                return
            old_status = payment.status
>>>>>>> 1d670fd (refactor)
            payment.status = self.STATUS_REJECTED
            payment.reviewed_at = timezone.now()
            payment.reviewed_by = user
            payment.save(update_fields=["status", "reviewed_at", "reviewed_by"])
<<<<<<< HEAD
=======
            payment._record_event(
                old_status=old_status,
                new_status=payment.status,
                user=user,
                note=payment.admin_note,
            )
>>>>>>> 1d670fd (refactor)

            membership = payment.membership
            membership.payment_status = "rejected"
            membership.is_approved = False
            membership.save(update_fields=["payment_status", "is_approved"])
<<<<<<< HEAD

=======
>>>>>>> 1d670fd (refactor)
            notify_payment_reviewed(payment)

            self.status = payment.status
            self.reviewed_at = payment.reviewed_at
            self.reviewed_by = payment.reviewed_by
<<<<<<< HEAD
=======


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
>>>>>>> 1d670fd (refactor)
