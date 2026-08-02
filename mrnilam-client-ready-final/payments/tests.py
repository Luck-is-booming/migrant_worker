from decimal import Decimal
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from core.models import Membership
from members.models import MembershipRecord

from .forms import ManualPaymentForm
from .models import ManualPayment, PaymentReviewEvent
from .tokens import make_membership_token, make_payment_token, read_membership_token, read_payment_token
from .views import get_membership_amount


def valid_image(name="proof.png"):
    buffer = BytesIO()
    Image.new("RGB", (2, 2), "white").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@override_settings(MANUAL_PAYMENT_CONFIG={"GENERAL_MEMBER_AMOUNT": "500", "LIFE_MEMBER_AMOUNT": "5000"}, EMAIL_NOTIFICATIONS_ENABLED=False)
class PaymentFlowTests(TestCase):
    def make_membership(self, **overrides):
        data = {"name": "परीक्षण सदस्य", "name_en": "Test Member", "email": "member@example.com", "municipality": "phakphokthum", "ward_no": 3, "address": "Phakphokthum", "designation": "Member", "destination_country": "Qatar", "phone": "9800000000", "membership_type": "general"}
        data.update(overrides)
        return Membership.objects.create(**data)

    def make_payment(self, membership):
        return ManualPayment.objects.create(membership=membership, amount=Decimal("500.00"), screenshot=valid_image())

    def test_amount_comes_from_settings(self):
        self.assertEqual(get_membership_amount(self.make_membership()), Decimal("500.00"))

    def test_signed_tokens_round_trip(self):
        membership = self.make_membership()
        payment = self.make_payment(membership)
        self.assertEqual(read_membership_token(make_membership_token(membership.id)), membership.id)
        self.assertEqual(read_payment_token(make_payment_token(payment.id)), payment.id)

    def test_approval_creates_normalized_membership_and_audit(self):
        membership = self.make_membership()
        payment = self.make_payment(membership)
        payment.approve()
        membership.refresh_from_db()
        record = MembershipRecord.objects.get(source_application=membership)
        self.assertEqual(record.organization_unit.name_en, "Phakphokthum Rural Municipality")
        self.assertEqual(record.category.code, "general")
        self.assertTrue(record.membership_number)
        self.assertTrue(membership.is_approved)
        self.assertTrue(PaymentReviewEvent.objects.filter(payment=payment, new_status="approved").exists())

    def test_approved_private_status_shows_issued_number(self):
        membership = self.make_membership()
        payment = self.make_payment(membership)
        payment.approve()
        record = MembershipRecord.objects.get(source_application=membership)

        response = self.client.get(
            reverse(
                "payments:payment_pending",
                kwargs={"token": make_payment_token(payment.id)},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, record.membership_number)
        self.assertContains(response, record.organization_unit.name_en)

    def test_repeated_approval_is_idempotent(self):
        membership = self.make_membership()
        payment = self.make_payment(membership)
        payment.approve()
        first = MembershipRecord.objects.get(source_application=membership)
        payment.approve()
        self.assertEqual(MembershipRecord.objects.filter(source_application=membership).count(), 1)
        self.assertEqual(
            MembershipRecord.objects.get(source_application=membership).membership_number,
            first.membership_number,
        )
        self.assertEqual(
            PaymentReviewEvent.objects.filter(payment=payment, new_status="approved").count(),
            1,
        )

    def test_only_one_open_payment_per_application(self):
        membership = self.make_membership()
        self.make_payment(membership)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_payment(membership)

    def test_rejection_requires_a_reason(self):
        membership = self.make_membership()
        payment = self.make_payment(membership)
        with self.assertRaises(ValidationError):
            payment.reject()

    def test_rejection_does_not_create_membership(self):
        membership = self.make_membership()
        payment = self.make_payment(membership)
        payment.rejection_reason = "The submitted proof could not be verified."
        payment.save(update_fields=["rejection_reason"])
        payment.reject()
        self.assertFalse(MembershipRecord.objects.filter(source_application=membership).exists())
        membership.refresh_from_db()
        self.assertEqual(membership.payment_status, "rejected")

    def test_duplicate_transaction_reference_is_rejected_by_form(self):
        membership = self.make_membership()
        ManualPayment.objects.create(
            membership=membership,
            amount=Decimal("500.00"),
            transaction_id="TX-100",
            screenshot=valid_image("first.png"),
            status=ManualPayment.STATUS_REJECTED,
        )
        form = ManualPaymentForm(
            data={"transaction_id": " tx 100 ", "note": ""},
            files={"screenshot": valid_image("second.png")},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("transaction_id", form.errors)

    def test_invalid_screenshot_is_rejected(self):
        form = ManualPaymentForm(
            data={"transaction_id": "TX-INVALID", "note": ""},
            files={
                "screenshot": SimpleUploadedFile(
                    "proof.png", b"not-an-image", content_type="image/png"
                )
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("screenshot", form.errors)
