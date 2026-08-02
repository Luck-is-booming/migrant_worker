import re

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Count, Q


def normalize_number(value):
    table = str.maketrans("०१२३४५६७८९", "0123456789")
    text = str(value or "").translate(table).strip().replace(" ", "").casefold()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text


def backfill_ledger(apps, schema_editor):
    Member = apps.get_model("members", "Member")
    MembershipRecord = apps.get_model("members", "MembershipRecord")
    Sequence = apps.get_model("members", "MembershipNumberSequence")
    Issue = apps.get_model("members", "MembershipNumberIssue")

    Member.objects.filter(status="unknown").update(status="active")
    MembershipRecord.objects.filter(status="unknown").update(status="active")

    duplicate_scopes = list(
        MembershipRecord.objects.exclude(membership_number_normalized="")
        .values(
            "category_id",
            "organization_unit_id",
            "membership_number_normalized",
        )
        .annotate(total=Count("id"))
        .filter(total__gt=1)[:20]
    )
    if duplicate_scopes:
        details = "; ".join(
            f"category={row['category_id']} unit={row['organization_unit_id']} "
            f"number={row['membership_number_normalized']} count={row['total']}"
            for row in duplicate_scopes
        )
        raise RuntimeError(
            "Duplicate membership numbers already exist inside the same registry "
            "scope. No rows were changed. Resolve these conflicts against the "
            f"source data and rerun the migration. Examples: {details}"
        )

    # Preserve imported source text while placing it into the likely language
    # column. This does not invent translations; missing counterparts remain
    # blank for an administrator to review.
    for record in MembershipRecord.objects.iterator():
        updates = {}
        for raw_name, ne_name, en_name in (
            ("designation", "designation_ne", "designation_en"),
            ("destination_country", "destination_country_ne", "destination_country_en"),
            ("address_display", "address_display_ne", "address_display_en"),
        ):
            raw = str(getattr(record, raw_name, "") or "").strip()
            if not raw:
                continue
            target = ne_name if re.search(r"[\u0900-\u097f]", raw) else en_name
            if not getattr(record, target, ""):
                updates[target] = raw
        if updates:
            MembershipRecord.objects.filter(pk=record.pk).update(**updates)

    maxima = {}
    for record in MembershipRecord.objects.select_related("category", "organization_unit").iterator():
        normalized = normalize_number(record.membership_number)
        if not normalized:
            continue
        number_int = int(normalized) if normalized.isdigit() else None
        Issue.objects.get_or_create(
            category_id=record.category_id,
            organization_unit_id=record.organization_unit_id,
            membership_number_normalized=normalized,
            defaults={
                "membership_number": record.membership_number,
                "number_int": number_int,
                "membership_id": record.pk,
                "source": "existing",
            },
        )
        if number_int is not None:
            key = (record.category_id, record.organization_unit_id)
            maxima[key] = max(maxima.get(key, 0), number_int)

    for (category_id, unit_id), highest in maxima.items():
        Sequence.objects.update_or_create(
            category_id=category_id,
            organization_unit_id=unit_id,
            defaults={"next_number": highest + 1},
        )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("members", "0007_membershiprecord_ordering"),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"), ("inactive", "Inactive"), ("pending", "Pending"),
                    ("expired", "Expired"), ("suspended", "Suspended"),
                    ("archived", "Archived"), ("rejected", "Rejected"),
                ],
                default="active",
                max_length=20,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="membershiprecord",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"), ("inactive", "Inactive"), ("pending", "Pending"),
                    ("expired", "Expired"), ("suspended", "Suspended"),
                    ("archived", "Archived"), ("rejected", "Rejected"),
                ],
                default="active",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="membershiprecord",
            name="archived_at",
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="membershiprecord",
            name="archived_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="archived_memberships",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="membershiprecord",
            name="designation_ne",
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name="membershiprecord",
            name="designation_en",
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name="membershiprecord",
            name="destination_country_ne",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="membershiprecord",
            name="destination_country_en",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="membershiprecord",
            name="address_display_ne",
            field=models.CharField(
                blank=True,
                help_text="General locality only; do not enter a private street address.",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="membershiprecord",
            name="address_display_en",
            field=models.CharField(
                blank=True,
                help_text="General locality only; do not enter a private street address.",
                max_length=255,
            ),
        ),
        migrations.CreateModel(
            name="MembershipNumberSequence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("next_number", models.PositiveBigIntegerField(default=1)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="number_sequences", to="members.membershipcategory")),
                ("organization_unit", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="number_sequences", to="members.organizationunit")),
            ],
            options={"verbose_name": "Membership number sequence", "verbose_name_plural": "Membership number sequences"},
        ),
        migrations.AddConstraint(
            model_name="membershipnumbersequence",
            constraint=models.UniqueConstraint(fields=("category", "organization_unit"), name="unique_membership_number_sequence_scope"),
        ),
        migrations.AddConstraint(
            model_name="membershipnumbersequence",
            constraint=models.CheckConstraint(condition=Q(next_number__gte=1), name="membership_sequence_next_number_positive"),
        ),
        migrations.CreateModel(
            name="MembershipNumberIssue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("membership_number", models.CharField(max_length=60)),
                ("membership_number_normalized", models.CharField(max_length=60)),
                ("number_int", models.PositiveBigIntegerField(blank=True, null=True)),
                ("source", models.CharField(default="system", max_length=30)),
                ("issued_at", models.DateTimeField(auto_now_add=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="number_issues", to="members.membershipcategory")),
                ("organization_unit", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="number_issues", to="members.organizationunit")),
                ("membership", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="number_issue", to="members.membershiprecord")),
                ("issued_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="issued_membership_numbers", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["organization_unit", "category", "number_int", "membership_number"],
                "verbose_name": "Issued membership number",
                "verbose_name_plural": "Issued membership numbers",
            },
        ),
        migrations.AddConstraint(
            model_name="membershipnumberissue",
            constraint=models.UniqueConstraint(fields=("category", "organization_unit", "membership_number_normalized"), name="unique_issued_membership_number_scope"),
        ),
        migrations.AddIndex(
            model_name="membershipnumberissue",
            index=models.Index(fields=["category", "organization_unit", "number_int"], name="members_num_issue_scope_idx"),
        ),
        migrations.RunPython(backfill_ledger, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="membershiprecord",
            constraint=models.UniqueConstraint(
                condition=~Q(membership_number_normalized=""),
                fields=("category", "organization_unit", "membership_number_normalized"),
                name="unique_membership_number_per_registry_scope",
            ),
        ),
    ]
