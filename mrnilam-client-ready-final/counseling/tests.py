import time

from django.core import signing
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import CounselingCategory, CounselingRequest


@override_settings(EMAIL_NOTIFICATIONS_ENABLED=False, COUNSELING_ATTACHMENTS_ENABLED=False)
class CounselingRequestTests(TestCase):
    def setUp(self):
        self.category, _ = CounselingCategory.objects.get_or_create(
            code="fraud",
            defaults={"name_ne": "ठगी", "name_en": "Fraud concern"},
        )

    def payload(self, **overrides):
        data = {
            "full_name": "Test Person",
            "phone": "+977 981-234-5678",
            "email": "",
            "preferred_language": "ne",
            "location": "Ilam",
            "category": self.category.pk,
            "message": "I need general guidance.",
            "preferred_contact_method": "phone",
            "availability": "Evening",
            "consent_to_contact": "on",
            "website": "",
            "form_started": signing.dumps(time.time() - 10, salt="counseling-form"),
        }
        data.update(overrides)
        return data

    def test_phone_and_consent_are_required(self):
        with translation.override("en"):
            response = self.client.post(reverse("counseling:request"), self.payload(phone="", consent_to_contact=""))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CounselingRequest.objects.count(), 0)

    def test_nepal_phone_is_normalized_and_request_is_private(self):
        with translation.override("en"):
            response = self.client.post(reverse("counseling:request"), self.payload())
        self.assertEqual(response.status_code, 302)
        request_obj = CounselingRequest.objects.get()
        self.assertEqual(request_obj.phone, "+9779812345678")
        self.assertNotContains(self.client.get("/en/"), "+9779812345678")

    def test_honeypot_blocks_spam(self):
        with translation.override("en"):
            response = self.client.post(reverse("counseling:request"), self.payload(website="spam.example"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CounselingRequest.objects.count(), 0)

    def test_explicit_international_phone_is_preserved(self):
        with translation.override("en"):
            response = self.client.post(
                reverse("counseling:request"),
                self.payload(phone="+91 98765 43210"),
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CounselingRequest.objects.get().phone, "+919876543210")


class CounselingAttachmentValidationTests(TestCase):
    def test_rejects_file_renamed_to_pdf(self):
        from django.core.exceptions import ValidationError
        from django.core.files.uploadedfile import SimpleUploadedFile

        from .validators import validate_private_attachment

        fake_pdf = SimpleUploadedFile(
            "evidence.pdf",
            b"this is not a PDF",
            content_type="application/pdf",
        )
        with self.assertRaises(ValidationError):
            validate_private_attachment(fake_pdf)

    def test_accepts_pdf_signature(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from .validators import validate_private_attachment

        pdf = SimpleUploadedFile(
            "evidence.pdf",
            b"%PDF-1.7\n% minimal test fixture",
            content_type="application/pdf",
        )
        validate_private_attachment(pdf)
        self.assertEqual(pdf.tell(), 0)
