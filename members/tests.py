from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from .models import Member


class PhakphokthumImportTests(TestCase):
    def test_imports_committee_docx(self):
        source = Path(settings.BASE_DIR) / "data" / "Phakphokthum Rural Commeetee.docx"
        call_command(
            "import_phakphokthum_committee",
            file=str(source),
            verbosity=0,
        )

        members = Member.objects.filter(
            level="rural_municipality",
            unit_name="Phakphokthum Rural Municipality",
        )
        self.assertEqual(members.count(), 11)
        self.assertTrue(members.filter(name_ne="लक्ष्मण घतानी", designation="अध्यक्ष").exists())
        self.assertTrue(members.filter(name_ne="गजेन्द्र कुमार राइ", designation="सदस्य").exists())
        self.assertTrue(members.filter(membership_number="1").exists())
        self.assertTrue(members.filter(membership_number="11").exists())
        self.assertFalse(members.filter(show_phone_publicly=True).exists())
