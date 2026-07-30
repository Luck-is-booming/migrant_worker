from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from core.models import Membership
from members.models import Member

from .models import ManualPayment
from .tokens import (
    make_membership_token,
    make_payment_token,
    read_membership_token,
    read_payment_token,
)
from .views import get_membership_amount


@override_settings(
    MANUAL_PAYMENT_CONFIG={
        "GENERAL_MEMBER_AMOUNT": "500",
        "LIFE_MEMBER_AMOUNT": "5000",
    },
    EMAIL_NOTIFICATIONS_ENABLED=False,
)
class PaymentFlowTests(TestCase):
    def make_membership(self, **overrides):
        data = {
            "name": "परीक्षण सदस्य",
            "name_en": "Test Member",
            "email": "member@example.com",
            "municipality": "phakphokthum",
            "ward_no": 3,
            "address": "Phakphokthum",
            "designation": "Member",
            "destination_country": "Qatar",
            "phone": "9800000000",
            "membership_type": "general",
        }
        data.update(overrides)
        return Membership.objects.create(**data)

    def test_amount_comes_from_settings(self):
        general = self.make_membership()
        life = self.make_membership(
            name="आजीवन सदस्य",
            email="life@example.com",
            membership_type="life",
        )
        self.assertEqual(get_membership_amount(general), Decimal("500.00"))
        self.assertEqual(get_membership_amount(life), Decimal("5000.00"))

    def test_signed_tokens_round_trip(self):
        membership = self.make_membership()
        payment = ManualPayment.objects.create(
            membership=membership,
            amount=Decimal("500.00"),
            screenshot=SimpleUploadedFile("proof.jpg", b"fake-image"),
        )
        self.assertEqual(
            read_membership_token(make_membership_token(membership.id)),
            membership.id,
        )
        self.assertEqual(
            read_payment_token(make_payment_token(payment.id)),
            payment.id,
        )

    def test_approval_creates_numeric_registry_member(self):
        membership = self.make_membership()
        payment = ManualPayment.objects.create(
            membership=membership,
            amount=Decimal("500.00"),
            transaction_id="TX-123",
            screenshot=SimpleUploadedFile("proof.jpg", b"fake-image"),
        )

        payment.approve()
        membership.refresh_from_db()
        member = Member.objects.get(source_membership=membership)

        self.assertEqual(payment.status, ManualPayment.STATUS_APPROVED)
        self.assertTrue(membership.is_approved)
        self.assertEqual(membership.payment_status, "completed")
        self.assertEqual(member.level, "rural_municipality")
        self.assertEqual(member.unit_name, "Phakphokthum Rural Municipality")
        self.assertEqual(member.membership_number, "1")
        self.assertNotIn("MWRWPC-", member.membership_number)
        self.assertFalse(member.show_phone_publicly)

    def test_reject_does_not_create_member(self):
        membership = self.make_membership()
        payment = ManualPayment.objects.create(
            membership=membership,
            amount=Decimal("500.00"),
            screenshot=SimpleUploadedFile("proof.jpg", b"fake-image"),
        )

        payment.reject()
        membership.refresh_from_db()

        self.assertEqual(payment.status, ManualPayment.STATUS_REJECTED)
        self.assertEqual(membership.payment_status, "rejected")
        self.assertFalse(membership.is_approved)
        self.assertFalse(Member.objects.filter(source_membership=membership).exists())
