from django.apps import apps
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


def get_member_level(municipality):
    rural_municipalities = [
        "phakphokthum",
        "sandakpur",
    ]

    if municipality in rural_municipalities:
        return "rural_municipality"

    return "municipality"


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

    # Keep this in database, but remove it from user-facing form.
    # Admin can use it later if needed.
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

    def approve(self, user=None):
        with transaction.atomic():
            self.status = self.STATUS_APPROVED
            self.reviewed_at = timezone.now()
            self.reviewed_by = user
            self.save(update_fields=[
                "status",
                "reviewed_at",
                "reviewed_by",
            ])

            self.membership.payment_status = "completed"
            self.membership.is_approved = True
            self.membership.amount = self.amount

            if self.transaction_id:
                self.membership.transaction_id = self.transaction_id

            self.membership.save(update_fields=[
                "payment_status",
                "is_approved",
                "amount",
                "transaction_id",
            ])

            Member = apps.get_model("members", "Member")

            generated_membership_number = f"MWRWPC-{self.membership.id:04d}"

            name_en = getattr(self.membership, "name_en", "") or self.membership.name
            ward_no = getattr(self.membership, "ward_no", None)
            address = getattr(self.membership, "address", "")
            designation = getattr(self.membership, "designation", "")
            destination_country = getattr(self.membership, "destination_country", "")
            phone = getattr(self.membership, "phone", "")

            member, created = Member.objects.get_or_create(
                membership_number=generated_membership_number,
                defaults={
                    "name_ne": self.membership.name,
                    "name_en": name_en,
                    "membership_type": self.membership.membership_type,
                    "status": "active",
                    "level": get_member_level(self.membership.municipality),
                    "municipality": self.membership.get_municipality_display(),
                    "ward_no": ward_no,
                    "address": address,
                    "designation": designation,
                    "destination_country": destination_country,
                    "phone": phone,
                    "is_public": True,
                },
            )

            if not created:
                member.name_ne = self.membership.name
                member.name_en = name_en
                member.membership_type = self.membership.membership_type
                member.status = "active"
                member.level = get_member_level(self.membership.municipality)
                member.municipality = self.membership.get_municipality_display()
                member.ward_no = ward_no
                member.address = address
                member.designation = designation
                member.destination_country = destination_country
                member.phone = phone
                member.is_public = True
                member.save()

    def reject(self, user=None):
        self.status = self.STATUS_REJECTED
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.save(update_fields=[
            "status",
            "reviewed_at",
            "reviewed_by",
        ])