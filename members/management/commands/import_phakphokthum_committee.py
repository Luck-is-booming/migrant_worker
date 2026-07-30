from pathlib import Path
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from docx import Document

from members.models import Member
from members.name_utils import romanize_nepali_name


NEPALI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
DEFAULT_FILE = Path("data") / "Phakphokthum Rural Commeetee.docx"
DEFAULT_UNIT = "Phakphokthum Rural Municipality"


def clean_text(value):
    return " ".join(str(value or "").replace("\xa0", " ").split()).strip()


def nepali_number_to_int(value):
    text = clean_text(value).translate(NEPALI_DIGITS)
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


def clean_phone(value):
    text = clean_text(value).translate(NEPALI_DIGITS)
    return re.sub(r"[^0-9+]", "", text)


class Command(BaseCommand):
    help = (
        "Import the 11-person Phakphokthum rural committee DOCX into the "
        "public members.Member registry."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=str(DEFAULT_FILE),
            help="DOCX path relative to manage.py, or an absolute path.",
        )
        parser.add_argument(
            "--membership-type",
            choices=["general", "life"],
            default="general",
            help=(
                "The source document does not state membership type. "
                "The importer defaults to general."
            ),
        )
        parser.add_argument(
            "--unit-name",
            default=DEFAULT_UNIT,
            help="Registry/unit name shown in the member-directory filter.",
        )
        parser.add_argument(
            "--show-phone",
            action="store_true",
            help="Show imported phone numbers publicly. Default: hidden.",
        )
        parser.add_argument(
            "--replace-unit",
            action="store_true",
            help="Delete current records in this exact registry before importing.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.is_absolute():
            file_path = Path(settings.BASE_DIR) / file_path

        if not file_path.exists():
            raise CommandError(f"DOCX file not found: {file_path}")

        document = Document(file_path)
        if not document.tables:
            raise CommandError("The DOCX does not contain a member table.")

        table = document.tables[0]
        rows = []
        for row in table.rows[1:]:
            cells = [clean_text(cell.text) for cell in row.cells]
            if len(cells) < 5:
                continue

            serial, designation, name, address, phone = cells[:5]
            if not name:
                continue

            rows.append({
                "serial": nepali_number_to_int(serial),
                "designation": designation,
                "name": name,
                "address": address,
                "phone": clean_phone(phone),
            })

        if not rows:
            raise CommandError("No committee members were found in the DOCX table.")

        unit_name = clean_text(options["unit_name"])
        membership_type = options["membership_type"]
        show_phone = options["show_phone"]

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            if options["replace_unit"]:
                deleted_count, _ = Member.objects.filter(
                    level="rural_municipality",
                    unit_name=unit_name,
                ).delete()
                self.stdout.write(
                    self.style.WARNING(
                        f"Deleted {deleted_count} existing rows from {unit_name}."
                    )
                )

            for row in rows:
                member = Member.objects.filter(
                    level="rural_municipality",
                    unit_name=unit_name,
                    name_ne=row["name"],
                ).first()

                if member is None:
                    member = Member(
                        level="rural_municipality",
                        unit_name=unit_name,
                        name_ne=row["name"],
                        membership_type=membership_type,
                    )
                    created = True
                else:
                    # The DOCX does not state membership type, so keep the type
                    # already assigned to an existing registry record.
                    created = False

                member.name_en = member.name_en or romanize_nepali_name(row["name"])
                member.status = "active"
                member.municipality = unit_name
                member.address = row["address"]
                member.designation = row["designation"]
                member.phone = row["phone"]
                member.show_phone_publicly = show_phone
                member.is_public = True
                member.sort_order = row["serial"]
                member.save()

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(rows)} committee rows: "
                f"{created_count} created, {updated_count} updated."
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "The DOCX does not provide membership type or membership numbers. "
                f"Type used: {membership_type}; new numbers were assigned inside "
                f"the {unit_name} registry."
            )
        )
        self.stdout.write(
            "Phone numbers were "
            + ("made public." if show_phone else "stored but hidden from the public directory.")
        )
