import re
import uuid
from difflib import SequenceMatcher

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


NEPALI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def _phone(value):
    digits = re.sub(r"\D", "", str(value or "").translate(NEPALI_DIGITS))
    if digits.startswith("977") and len(digits) >= 12:
        digits = digits[3:]
    return digits


def _name(value):
    text = str(value or "").casefold().replace("रकम", "")
    return re.sub(r"[^\w\u0900-\u097f]+", "", text)


def _strong_name_match(left, right):
    a, b = _name(left), _name(right)
    if not a or not b:
        return False
    return a == b or a in b or b in a or SequenceMatcher(None, a, b).ratio() >= 0.76


def backfill_registry(apps, schema_editor):
    LegacyMember = apps.get_model("members", "Member")
    Person = apps.get_model("members", "Person")
    Category = apps.get_model("members", "MembershipCategory")
    Unit = apps.get_model("members", "OrganizationUnit")
    Membership = apps.get_model("members", "MembershipRecord")
    Duplicate = apps.get_model("members", "PotentialDuplicate")

    categories = {
        "life": Category.objects.get_or_create(
            code="life",
            defaults={"name_ne": "आजीवन सदस्य", "name_en": "Life Member", "display_order": 1},
        )[0],
        "general": Category.objects.get_or_create(
            code="general",
            defaults={"name_ne": "साधारण सदस्य", "name_en": "General Member", "display_order": 2},
        )[0],
    }

    for legacy in LegacyMember.objects.all().order_by("pk"):
        phone = _phone(legacy.phone)
        candidates = list(Person.objects.filter(phone=phone)) if phone else []
        strong = [person for person in candidates if _strong_name_match(legacy.name_ne, person.name_ne)]

        if len(strong) == 1:
            person = strong[0]
        else:
            person = Person.objects.create(
                name_ne=legacy.name_ne,
                name_en=legacy.name_en,
                normalized_name=_name(legacy.name_ne or legacy.name_en),
                phone=phone,
                location=legacy.address or legacy.municipality,
                needs_identity_review=bool(candidates),
            )
            for candidate in candidates:
                a, b = sorted([person, candidate], key=lambda item: item.pk)
                Duplicate.objects.get_or_create(
                    person_a=a,
                    person_b=b,
                    defaults={
                        "signals": {
                            "same_phone": phone,
                            "name_a": a.name_ne,
                            "name_b": b.name_ne,
                        }
                    },
                )

        unit_name = legacy.unit_name or legacy.municipality or "Unknown Unit"
        unit, _ = Unit.objects.get_or_create(
            level=legacy.level or "unknown",
            name_en=unit_name,
            defaults={"slug": f"legacy-unit-{legacy.pk}"},
        )
        category = categories.get(legacy.membership_type) or Category.objects.get_or_create(
            code=legacy.membership_type or "other",
            defaults={
                "name_ne": legacy.membership_type or "अन्य",
                "name_en": (legacy.membership_type or "Other").title(),
                "display_order": 50,
            },
        )[0]

        normalized_number = str(legacy.membership_number or "").strip().casefold()
        number_int = int(normalized_number) if normalized_number.isdigit() else None
        Membership.objects.get_or_create(
            legacy_member=legacy,
            defaults={
                "public_id": uuid.uuid4(),
                "person": person,
                "category": category,
                "organization_unit": unit,
                "membership_number": legacy.membership_number,
                "membership_number_normalized": normalized_number,
                "membership_number_int": number_int,
                "status": legacy.status or "unknown",
                "designation": legacy.designation,
                "destination_country": legacy.destination_country,
                "address_display": legacy.address or legacy.municipality,
                "is_public": legacy.is_public,
                "source_application": legacy.source_membership,
            },
        )


def reverse_backfill(apps, schema_editor):
    # Preserve normalized audit data during code rollbacks.
    pass


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0012_membership_email"),
        ("members", "0005_member_source_membership"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("source_file_name", models.CharField(max_length=255)),
                ("source_checksum", models.CharField(db_index=True, max_length=64)),
                ("source_sheet", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("dry_run", "Dry run"), ("completed", "Completed"), ("failed", "Failed"), ("rolled_back", "Rolled back")], default="pending", max_length=20)),
                ("is_dry_run", models.BooleanField(default=False)),
                ("options", models.JSONField(blank=True, default=dict)),
                ("summary", models.JSONField(blank=True, default=dict)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="member_import_batches", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-started_at"], "verbose_name": "Member import batch", "verbose_name_plural": "Member import batches"},
        ),
        migrations.CreateModel(
            name="MembershipCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=40, unique=True)),
                ("name_ne", models.CharField(max_length=100)),
                ("name_en", models.CharField(max_length=100)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["display_order", "name_en"], "verbose_name": "Membership category", "verbose_name_plural": "Membership categories"},
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("name_ne", models.CharField(max_length=180, verbose_name="Name (Nepali)")),
                ("name_en", models.CharField(blank=True, max_length=180, verbose_name="Name (English)")),
                ("normalized_name", models.CharField(blank=True, db_index=True, editable=False, max_length=220)),
                ("phone", models.CharField(blank=True, help_text="Never shown in the public member directory.", max_length=24, verbose_name="Private phone number")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Private email address")),
                ("location", models.CharField(blank=True, max_length=255)),
                ("is_public", models.BooleanField(default=True)),
                ("needs_identity_review", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name_ne", "name_en"], "verbose_name": "Person", "verbose_name_plural": "People"},
        ),
        migrations.AddField(
            model_name="person",
            name="merged_into",
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="merged_people", to="members.person"),
        ),
        migrations.CreateModel(
            name="OrganizationUnit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("level", models.CharField(choices=[("district", "District"), ("municipality", "Municipality"), ("rural_municipality", "Rural Municipality"), ("ward", "Ward"), ("unknown", "Unknown"), ("other", "Other")], default="unknown", max_length=30)),
                ("name_ne", models.CharField(blank=True, max_length=180)),
                ("name_en", models.CharField(max_length=180)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("geographic_name", models.CharField(blank=True, max_length=180)),
                ("is_active", models.BooleanField(default=True)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="children", to="members.organizationunit")),
            ],
            options={"ordering": ["display_order", "level", "name_en"], "verbose_name": "Organization unit", "verbose_name_plural": "Organization units"},
        ),
        migrations.AddConstraint(model_name="organizationunit", constraint=models.UniqueConstraint(fields=("level", "name_en"), name="unique_organization_unit_level_name")),
        migrations.CreateModel(
            name="MembershipRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("membership_number", models.CharField(blank=True, max_length=60)),
                ("membership_number_normalized", models.CharField(blank=True, db_index=True, editable=False, max_length=60)),
                ("membership_number_int", models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ("source_identity_key", models.CharField(blank=True, db_index=True, editable=False, max_length=160)),
                ("status", models.CharField(choices=[("active", "Active"), ("expired", "Expired"), ("unknown", "Unknown"), ("archived", "Archived")], default="unknown", max_length=20)),
                ("joined_date", models.DateField(blank=True, null=True)),
                ("designation", models.CharField(blank=True, max_length=180)),
                ("destination_country", models.CharField(blank=True, max_length=150)),
                ("address_display", models.CharField(blank=True, help_text="General locality only; do not enter a private street address.", max_length=255)),
                ("is_public", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="memberships", to="members.membershipcategory")),
                ("created_by_import", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_memberships", to="members.importbatch")),
                ("legacy_member", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="normalized_membership", to="members.member")),
                ("organization_unit", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="memberships", to="members.organizationunit")),
                ("person", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="memberships", to="members.person")),
                ("source_application", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="normalized_membership", to="core.membership")),
            ],
            options={"verbose_name": "Membership", "verbose_name_plural": "Memberships"},
        ),
        migrations.AddConstraint(model_name="membershiprecord", constraint=models.UniqueConstraint(condition=~Q(source_identity_key=""), fields=("organization_unit", "source_identity_key"), name="unique_membership_source_identity_per_unit")),
        migrations.CreateModel(
            name="ImportRowRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("row_number", models.PositiveIntegerField()),
                ("row_checksum", models.CharField(blank=True, max_length=64)),
                ("status", models.CharField(choices=[("imported", "Imported"), ("updated", "Updated"), ("unchanged", "Unchanged"), ("duplicate", "Potential duplicate"), ("warning", "Imported with warnings"), ("failed", "Failed"), ("skipped", "Non-data row")], max_length=20)),
                ("original_data", models.JSONField(default=dict)),
                ("normalized_data", models.JSONField(default=dict)),
                ("warnings", models.JSONField(blank=True, default=list)),
                ("error_message", models.TextField(blank=True)),
                ("created_person", models.BooleanField(default=False)),
                ("created_membership", models.BooleanField(default=False)),
                ("before_person", models.JSONField(blank=True, default=dict)),
                ("before_membership", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rows", to="members.importbatch")),
                ("membership", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="import_rows", to="members.membershiprecord")),
                ("person", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="import_rows", to="members.person")),
            ],
            options={"ordering": ["batch", "row_number"]},
        ),
        migrations.AddConstraint(model_name="importrowrecord", constraint=models.UniqueConstraint(fields=("batch", "row_number"), name="unique_import_row_number_per_batch")),
        migrations.CreateModel(
            name="PotentialDuplicate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("signals", models.JSONField(blank=True, default=dict)),
                ("status", models.CharField(choices=[("pending", "Pending review"), ("same", "Confirmed same person"), ("different", "Confirmed different people"), ("dismissed", "Dismissed")], default="pending", max_length=20)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("person_a", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="duplicate_as_a", to="members.person")),
                ("person_b", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="duplicate_as_b", to="members.person")),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["status", "-created_at"]},
        ),
        migrations.AddConstraint(model_name="potentialduplicate", constraint=models.UniqueConstraint(fields=("person_a", "person_b"), name="unique_potential_duplicate_pair")),
        migrations.AddConstraint(model_name="potentialduplicate", constraint=models.CheckConstraint(condition=~Q(person_a=models.F("person_b")), name="potential_duplicate_people_must_differ")),
        migrations.AddIndex(model_name="importbatch", index=models.Index(fields=["source_checksum", "status"], name="members_imp_source__dcd5f8_idx")),
        migrations.AddIndex(model_name="person", index=models.Index(fields=["is_public", "normalized_name"], name="members_per_is_publ_4f7d57_idx")),
        migrations.AddIndex(model_name="person", index=models.Index(fields=["phone"], name="members_per_phone_607f3f_idx")),
        migrations.AddIndex(model_name="membershiprecord", index=models.Index(fields=["person", "status", "is_public"], name="members_mem_person__7aa822_idx")),
        migrations.AddIndex(model_name="membershiprecord", index=models.Index(fields=["category", "organization_unit"], name="members_mem_categor_57ea25_idx")),
        migrations.AddIndex(model_name="membershiprecord", index=models.Index(fields=["organization_unit", "membership_number_int"], name="members_mem_organiz_e4fc75_idx")),
        migrations.RunPython(backfill_registry, reverse_backfill),
    ]
