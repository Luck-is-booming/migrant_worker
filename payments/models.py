from django.apps import apps
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


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
    )


class ManualPayment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    membership = models.ForeignKey(
        "core.Membership",
        on_delete=models.CASCADE,
        related_name="manual_payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
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
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    admin_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.membership.name} - Rs. {self.amount} - {self.status}"

    @staticmethod
    def _member_address(membership, unit_name):
        address = (membership.address or "").strip()
        ward = membership.ward_no

        if not address:
            address = unit_name

        if ward and str(ward) not in address:
            address = f"{address} - Ward {ward}"

        return address

    def _create_or_update_member(self):
        Member = apps.get_model("members", "Member")
        from members.name_utils import romanize_nepali_name

        membership = self.membership
        level, unit_name = get_member_registry(membership.municipality)

        member = Member.objects.filter(source_membership=membership).first()

        # Attach records produced by the older MWRWPC-0001 numbering logic,
        # instead of creating a duplicate after this upgrade.
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

        return member

    def approve(self, user=None):
        from core.notifications import notify_payment_reviewed

        with transaction.atomic():
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

            self.status = payment.status
            self.reviewed_at = payment.reviewed_at
            self.reviewed_by = payment.reviewed_by

    def reject(self, user=None):
        from core.notifications import notify_payment_reviewed

        with transaction.atomic():
            payment = type(self).objects.select_for_update().select_related(
                "membership"
            ).get(pk=self.pk)

            # Do not accidentally undo an already approved membership or
            # resend rejection notifications for an unchanged decision.
            if payment.status in {self.STATUS_APPROVED, self.STATUS_REJECTED}:
                return

            payment.status = self.STATUS_REJECTED
            payment.reviewed_at = timezone.now()
            payment.reviewed_by = user
            payment.save(update_fields=["status", "reviewed_at", "reviewed_by"])

            membership = payment.membership
            membership.payment_status = "rejected"
            membership.is_approved = False
            membership.save(update_fields=["payment_status", "is_approved"])

            notify_payment_reviewed(payment)

            self.status = payment.status
            self.reviewed_at = payment.reviewed_at
            self.reviewed_by = payment.reviewed_by
