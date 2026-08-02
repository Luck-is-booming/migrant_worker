import tempfile
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError
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
    def test_member_directory_sorts_membership_numbers_numerically(self):
        self.create_person(100)
        self.create_person(2)
        self.create_person(10)

        with translation.override("en"):
            response = self.client.get(
                reverse("members:member_list"),
                {"category": self.category.code, "unit": self.unit.slug},
            )

        people = list(response.context["page_obj"].object_list)
        membership_numbers = [
            person.public_memberships[0].membership_number
            for person in people
        ]
        self.assertEqual(membership_numbers, ["2", "10", "100"])



class MembershipNumberingTests(TestCase):
    def setUp(self):
        self.category = MembershipCategory.objects.create(
            code="numbering-general",
            name_ne="साधारण सदस्य",
            name_en="General Member",
        )
        self.unit = OrganizationUnit.objects.create(
            level="district",
            name_ne="इलाम जिल्ला",
            name_en="Ilam District Numbering",
        )
        self.person = Person.objects.create(
            name_ne="नम्बर परीक्षण",
            name_en="Number Test",
        )

    def create_membership(self, **overrides):
        values = {
            "person": self.person,
            "category": self.category,
            "organization_unit": self.unit,
            "status": "active",
        }
        values.update(overrides)
        return MembershipRecord.objects.create(**values)

    def test_automatic_number_is_stable_when_profile_is_edited(self):
        record = self.create_membership()
        issued = record.membership_number
        record.designation = "Updated role"
        record.save()
        record.refresh_from_db()
        self.assertEqual(record.membership_number, issued)

    def test_archiving_and_restoring_preserves_number(self):
        record = self.create_membership()
        issued = record.membership_number
        record.archive()
        record.refresh_from_db()
        self.assertEqual(record.status, "archived")
        self.assertEqual(record.membership_number, issued)
        record.restore()
        record.refresh_from_db()
        self.assertEqual(record.status, "active")
        self.assertTrue(record.is_public)
        self.assertEqual(record.membership_number, issued)


    def test_private_membership_remains_private_after_archive_and_restore(self):
        record = self.create_membership(is_public=False)
        record.archive()
        record.restore()
        record.refresh_from_db()
        self.assertEqual(record.status, "active")
        self.assertFalse(record.is_public)

    def test_deleted_number_is_not_reused(self):
        first = self.create_membership()
        first_number = int(first.membership_number)
        first.delete()
        second = self.create_membership()
        self.assertEqual(int(second.membership_number), first_number + 1)

    def test_duplicate_explicit_number_is_rejected(self):
        self.create_membership(membership_number="25")
        other = Person.objects.create(name_ne="अर्को व्यक्ति", name_en="Other Person")
        with self.assertRaises((ValidationError, IntegrityError)):
            MembershipRecord.objects.create(
                person=other,
                category=self.category,
                organization_unit=self.unit,
                membership_number="25",
                status="active",
            )
        self.assertEqual(
            MembershipRecord.objects.filter(
                category=self.category,
                organization_unit=self.unit,
                membership_number_normalized="25",
            ).count(),
            1,
        )

    def test_one_person_can_receive_separate_numbers_in_multiple_categories(self):
        life = MembershipCategory.objects.create(
            code="numbering-life",
            name_ne="आजीवन सदस्य",
            name_en="Life Member",
        )
        general_record = self.create_membership()
        life_record = MembershipRecord.objects.create(
            person=self.person,
            category=life,
            organization_unit=self.unit,
            status="active",
        )
        self.assertEqual(general_record.membership_number, "1")
        self.assertEqual(life_record.membership_number, "1")
        self.assertEqual(self.person.memberships.count(), 2)


class ArchivedMemberVisibilityTests(TestCase):
    def test_archived_membership_is_not_public(self):
        category = MembershipCategory.objects.create(
            code="archived-general", name_ne="साधारण", name_en="General"
        )
        unit = OrganizationUnit.objects.create(
            level="district", name_ne="इलाम", name_en="Archived Test District"
        )
        person = Person.objects.create(name_ne="लुकाइएको", name_en="Archived Person")
        record = MembershipRecord.objects.create(
            person=person,
            category=category,
            organization_unit=unit,
            status="active",
            is_public=True,
        )
        record.archive()
        with translation.override("en"):
            response = self.client.get(reverse("members:member_list"))
        self.assertNotContains(response, person.name_en)

    def test_person_with_active_and_archived_membership_remains_public(self):
        category = MembershipCategory.objects.create(
            code="mixed-status-general", name_ne="साधारण", name_en="General"
        )
        life = MembershipCategory.objects.create(
            code="mixed-status-life", name_ne="आजीवन", name_en="Life"
        )
        unit = OrganizationUnit.objects.create(
            level="district", name_ne="इलाम जिल्ला", name_en="Mixed Status District"
        )
        person = Person.objects.create(name_ne="सक्रिय व्यक्ति", name_en="Active Person")
        MembershipRecord.objects.create(
            person=person, category=category, organization_unit=unit,
            status="active", is_public=True,
        )
        archived = MembershipRecord.objects.create(
            person=person, category=life, organization_unit=unit,
            status="active", is_public=True,
        )
        archived.archive()

        with translation.override("en"):
            listing = self.client.get(reverse("members:member_list"))
            detail = self.client.get(
                reverse("members:member_detail", kwargs={"public_id": person.public_id})
            )

        self.assertContains(listing, person.name_en)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(listing.context["result_count"], 1)
        listed = list(listing.context["page_obj"].object_list)[0]
        self.assertEqual(len(listed.public_memberships), 1)
        self.assertEqual(listed.public_memberships[0].status, "active")


import threading
import unittest

from django.db import close_old_connections, connection
from django.test import TransactionTestCase


@unittest.skipUnless(
    connection.vendor == "postgresql",
    "Concurrent allocator verification requires PostgreSQL; set TEST_DATABASE_URL.",
)
class PostgreSQLMembershipNumberConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def test_two_simultaneous_creations_receive_different_numbers(self):
        category = MembershipCategory.objects.create(
            code="concurrent-general", name_ne="साधारण", name_en="General"
        )
        unit = OrganizationUnit.objects.create(
            level="district", name_ne="इलाम", name_en="Concurrency District"
        )
        barrier = threading.Barrier(2)
        numbers = []
        failures = []

        def create_record(index):
            close_old_connections()
            try:
                person = Person.objects.create(
                    name_ne=f"समवर्ती {index}", name_en=f"Concurrent {index}"
                )
                barrier.wait(timeout=10)
                record = MembershipRecord.objects.create(
                    person=person,
                    category_id=category.pk,
                    organization_unit_id=unit.pk,
                    status="active",
                )
                numbers.append(record.membership_number)
            except Exception as exc:  # Captured and asserted in the main test thread.
                failures.append(exc)
            finally:
                close_old_connections()

        threads = [threading.Thread(target=create_record, args=(index,)) for index in (1, 2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=20)

        self.assertFalse(failures, failures)
        self.assertCountEqual(numbers, ["1", "2"])
