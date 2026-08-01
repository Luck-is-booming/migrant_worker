<<<<<<< HEAD
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
=======
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from openpyxl import Workbook

from .importing import WorkbookMemberImporter
from .models import (
    MembershipCategory,
    MembershipRecord,
    OrganizationUnit,
    Person,
    PotentialDuplicate,
)


class WorkbookImportTests(TestCase):
    def make_workbook(self, rows, filename="members.xlsx"):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / filename
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Members"
        sheet.append(["आप्रवासी कामदार हकहित संरक्षण केन्द्र, जिल्ला कार्यसमिति इलाम"])
        sheet.append(["सदस्यता अभिलेख"])
        sheet.append([
            "s.n", "नाम/थर", "ठेगाना", "पद", "सदस्यता नं.",
            "मिति", "प्रकार", "गएको देश", "सम्पर्क नम्वर", "कैफियत",
        ])
        for row in rows:
            sheet.append(row)
        workbook.save(path)
        self.addCleanup(directory.cleanup)
        return path

    def test_one_person_can_hold_general_and_life_memberships(self):
        path = self.make_workbook([
            [1, "नविन सुन्दर सेर्मा", "इलाम-७", "अध्यक्ष", 4, "2081/03/04", "आजिवन", "Korea", "9817913334", "active"],
            [2, "नविन सुनदर सेर्मा रकम", "इलाम-७", "सदस्य", 9, "2081/03/04", "साधारण", "Korea", "+977 981-791-3334", "active"],
        ])
        _, summary, _ = WorkbookMemberImporter(path, level="district", unit_name="Ilam District").run()
        self.assertEqual(summary.valid_data_rows, 2)
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(MembershipRecord.objects.count(), 2)
        person = Person.objects.get()
        self.assertSetEqual(set(person.memberships.values_list("category__code", flat=True)), {"life", "general"})

    def test_same_name_alone_does_not_merge_people(self):
        path = self.make_workbook([
            [1, "राम लिम्बु", "इलाम-१", "सदस्य", 1, "", "साधारण", "", "9800000001", "active"],
            [2, "राम लिम्बु", "इलाम-२", "सदस्य", 2, "", "साधारण", "", "9800000002", "active"],
        ])
        WorkbookMemberImporter(path, level="district", unit_name="Ilam District").run()
        self.assertEqual(Person.objects.count(), 2)
        self.assertEqual(MembershipRecord.objects.count(), 2)

    def test_rerun_is_idempotent_and_deletes_nothing(self):
        path = self.make_workbook([[1, "परीक्षण सदस्य", "इलाम", "सदस्य", 1, "", "साधारण", "", "9800000000", "active"]])
        WorkbookMemberImporter(path, level="district", unit_name="Ilam District").run()
        before = (Person.objects.count(), MembershipRecord.objects.count())
        _, summary, _ = WorkbookMemberImporter(path, level="district", unit_name="Ilam District").run()
        self.assertEqual(before, (Person.objects.count(), MembershipRecord.objects.count()))
        self.assertEqual(summary.records_deleted, 0)
        self.assertEqual(summary.unchanged_records, 1)

    def test_dry_run_commits_no_people_or_memberships(self):
        path = self.make_workbook([[1, "ड्राइ रन", "इलाम", "सदस्य", 1, "", "साधारण", "", "9800000000", "active"]])
        batch, summary, _ = WorkbookMemberImporter(path, level="district", unit_name="Ilam District", dry_run=True).run()
        self.assertEqual(batch.status, "dry_run")
        self.assertEqual(Person.objects.count(), 0)
        self.assertEqual(MembershipRecord.objects.count(), 0)
        self.assertEqual(summary.imported_memberships, 1)

    def test_conflicting_membership_number_is_reported_not_overwritten(self):
        path = self.make_workbook([
            [1, "पहिलो व्यक्ति", "इलाम", "सदस्य", 1, "", "साधारण", "", "9800000001", "active"],
            [2, "फरक व्यक्ति", "इलाम", "सदस्य", 1, "", "साधारण", "", "9800000002", "active"],
        ])
        _, summary, outcomes = WorkbookMemberImporter(path, level="district", unit_name="Ilam District").run()
        self.assertEqual(summary.failed_rows, 1)
        self.assertIn("Membership identifier conflict", outcomes[1].error)
        self.assertEqual(MembershipRecord.objects.count(), 0)

    def test_name_only_summary_row_is_audited_not_imported(self):
        path = self.make_workbook([[None, "आजिवन सदस्य - 54", None, None, None, None, None, None, None, None]])
        batch, summary, outcomes = WorkbookMemberImporter(
            path, level="municipality", unit_name="Ilam Municipality"
        ).run()
        self.assertEqual(summary.valid_data_rows, 0)
        self.assertEqual(summary.non_data_rows, 1)
        self.assertEqual(outcomes[0].status, "skipped")
        self.assertEqual(MembershipRecord.objects.count(), 0)
        self.assertEqual(batch.rows.get().status, "skipped")


class PhakphokthumImportTests(TestCase):
    def test_imports_all_committee_rows_without_public_phones(self):
        source = Path(__file__).resolve().parents[1] / "data" / "Phakphokthum Rural Commeetee.docx"
        call_command("import_phakphokthum_committee", file=str(source), verbosity=0)
        records = MembershipRecord.objects.filter(organization_unit__name_en="Phakphokthum Rural Municipality")
        self.assertEqual(records.count(), 11)
        self.assertFalse(records.filter(person__phone="").count() == 11)

class PublicMemberDirectoryTests(TestCase):
    def setUp(self):
        self.category = MembershipCategory.objects.create(
            code="general-test",
            name_ne="साधारण सदस्य",
            name_en="General Member",
        )
        self.unit = OrganizationUnit.objects.create(
            level="municipality",
            name_ne="इलाम नगरपालिका",
            name_en="Ilam Municipality Test",
        )

    def create_person(self, index, *, is_public=True, membership_public=True):
        person = Person.objects.create(
            name_ne=f"परीक्षण सदस्य {index}",
            name_en=f"Test Member {index}",
            phone=f"980000{index:04d}",
            email=f"private{index}@example.com",
            location="Private internal location",
            is_public=is_public,
        )
        MembershipRecord.objects.create(
            person=person,
            category=self.category,
            organization_unit=self.unit,
            membership_number=str(index),
            status="active",
            designation="Member",
            address_display="Ilam",
            is_public=membership_public,
        )
        return person

    def test_public_pages_never_display_private_contact_fields(self):
        person = self.create_person(1)
        with translation.override("en"):
            list_response = self.client.get(reverse("members:member_list"))
            detail_response = self.client.get(
                reverse("members:member_detail", kwargs={"public_id": person.public_id})
            )
        for response in (list_response, detail_response):
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, person.phone)
            self.assertNotContains(response, person.email)
            self.assertNotContains(response, "Private internal location")

    def test_private_person_and_private_membership_are_hidden(self):
        private_person = self.create_person(2, is_public=False)
        private_membership_person = self.create_person(3, membership_public=False)
        with translation.override("en"):
            response = self.client.get(reverse("members:member_list"))
            private_detail = self.client.get(
                reverse("members:member_detail", kwargs={"public_id": private_person.public_id})
            )
            private_membership_detail = self.client.get(
                reverse(
                    "members:member_detail",
                    kwargs={"public_id": private_membership_person.public_id},
                )
            )
        self.assertNotContains(response, private_person.name_en)
        self.assertNotContains(response, private_membership_person.name_en)
        self.assertEqual(private_detail.status_code, 404)
        self.assertEqual(private_membership_detail.status_code, 404)

    def test_search_filter_and_pagination_preserve_public_results(self):
        for index in range(1, 23):
            self.create_person(index)
        with translation.override("en"):
            first_page = self.client.get(reverse("members:member_list"))
            second_page = self.client.get(reverse("members:member_list"), {"page": 2})
            search = self.client.get(
                reverse("members:member_list"),
                {"q": "Test Member 22", "category": self.category.code},
            )
        self.assertEqual(first_page.context["page_obj"].paginator.count, 22)
        self.assertEqual(len(first_page.context["page_obj"].object_list), 20)
        self.assertEqual(len(second_page.context["page_obj"].object_list), 2)
        self.assertContains(search, "Test Member 22")
        self.assertEqual(search.context["result_count"], 1)

>>>>>>> 1d670fd (refactor)
