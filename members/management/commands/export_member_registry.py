import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from members.models import MembershipRecord


class Command(BaseCommand):
    help = "Export the normalized member registry as CSV or JSON without private audit data."

    def add_arguments(self, parser):
        parser.add_argument("output")
        parser.add_argument("--format", choices=["csv", "json"], default="csv")
        parser.add_argument("--include-private-contact", action="store_true")

    def handle(self, *args, **options):
        path = Path(options["output"]).expanduser().resolve()
        if path.exists():
            raise CommandError(f"Refusing to overwrite existing file: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        include_private = options["include_private_contact"]
        rows = []
        queryset = MembershipRecord.objects.select_related(
            "person", "category", "organization_unit"
        ).order_by(
            "organization_unit__display_order",
            "organization_unit__name_en",
            "category__display_order",
            "membership_number_int",
            "membership_number_normalized",
        )
        for record in queryset.iterator(chunk_size=500):
            row = {
                "person_public_id": str(record.person.public_id),
                "name_ne": record.person.name_ne,
                "name_en": record.person.name_en,
                "membership_category": record.category.code,
                "membership_category_en": record.category.name_en,
                "membership_category_ne": record.category.name_ne,
                "organization_level": record.organization_unit.level,
                "organization_unit_en": record.organization_unit.name_en,
                "organization_unit_ne": record.organization_unit.name_ne,
                "membership_number": record.membership_number,
                "status": record.status,
                "joined_date": record.joined_date.isoformat() if record.joined_date else "",
                "designation_ne": record.designation_ne,
                "designation_en": record.designation_en,
                "general_locality_ne": record.address_display_ne,
                "general_locality_en": record.address_display_en,
                "destination_country_ne": record.destination_country_ne,
                "destination_country_en": record.destination_country_en,
                "is_public": record.is_public,
            }
            if include_private:
                row["private_phone"] = record.person.phone
                row["private_email"] = record.person.email
            rows.append(row)

        if options["format"] == "json":
            path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            fieldnames = list(rows[0]) if rows else ["person_public_id", "membership_number"]
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        self.stdout.write(self.style.SUCCESS(f"Exported {len(rows)} memberships to {path}"))
