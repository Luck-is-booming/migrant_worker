import re
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, Q
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.i18n_utils import localized


NEPALI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def normalize_membership_number(value):
    """Normalize for comparison without changing the original display value."""
    text = str(value or "").translate(NEPALI_DIGITS).strip()
    text = re.sub(r"\s+", "", text)
    if re.fullmatch(r"\d+\.0+", text):
        text = text.split(".", 1)[0]
    return text.casefold()


def membership_number_as_int(value):
    normalized = normalize_membership_number(value)
    return int(normalized) if normalized.isdigit() else None


def normalize_person_name(value):
    text = str(value or "").strip().casefold()
    text = re.sub(r"[^\w\u0900-\u097f]+", "", text, flags=re.UNICODE)
    return text


class Member(models.Model):
    """Legacy member row retained for compatibility and audit preservation.

    New public functionality uses Person and MembershipRecord. This table is
    intentionally preserved so existing production records and historic IDs are
    never discarded during the normalization migration.
    """

    source_membership = models.OneToOneField(
        "core.Membership",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="member_record",
        verbose_name=_("Source membership application"),
    )

    MEMBERSHIP_TYPE_CHOICES = [
        ("life", _("Life Member")),
        ("general", _("General Member")),
    ]
    STATUS_CHOICES = [
        ("active", _("Active")),
        ("expired", _("Expired")),
        ("unknown", _("Unknown")),
    ]
    LEVEL_CHOICES = [
        ("district", _("District")),
        ("municipality", _("Municipality")),
        ("rural_municipality", _("Rural Municipality")),
        ("ward", _("Ward")),
        ("unknown", _("Unknown")),
    ]

    name_ne = models.CharField(max_length=150, verbose_name=_("Name (Nepali)"))
    name_en = models.CharField(max_length=150, blank=True, verbose_name=_("Name (English)"))
    membership_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Membership Number"),
        help_text=_(
            "Isolated inside Level + Unit + Membership Type. Example: District "
            "life no. 4 and Ilam Municipality life no. 1 can both exist."
        ),
    )
    membership_number_int = models.PositiveIntegerField(
        blank=True,
        null=True,
        editable=False,
        verbose_name=_("Membership Number for Sorting"),
    )
    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_TYPE_CHOICES,
        default="general",
        verbose_name=_("Membership Type"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="unknown",
        verbose_name=_("Status"),
    )
    level = models.CharField(
        max_length=30,
        choices=LEVEL_CHOICES,
        default="unknown",
        verbose_name=_("Organization Level"),
    )
    unit_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Committee / Unit Name"),
        help_text=_("Example: Ilam District, Ilam Municipality"),
    )
    municipality = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Municipality / Rural Municipality"),
    )
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Address"))
    designation = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Designation / Position"),
    )
    destination_country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Foreign Employment Country"),
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone Number"))
    show_phone_publicly = models.BooleanField(
        default=False,
        verbose_name=_("Show Phone Publicly"),
    )
    is_public = models.BooleanField(default=True, verbose_name=_("Show on Website"))
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text=_("Lower numbers display first."),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            "level",
            "unit_name",
            "membership_type",
            "membership_number_int",
            "sort_order",
            "name_ne",
        ]
        verbose_name = _("Legacy member record")
        verbose_name_plural = _("Legacy member records")
        indexes = [
            models.Index(fields=["level"]),
            models.Index(fields=["unit_name"]),
            models.Index(fields=["membership_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["municipality"]),
            models.Index(fields=["is_public"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "level",
                    "unit_name",
                    "membership_type",
                    "membership_number_int",
                ],
                condition=Q(membership_number_int__isnull=False),
                name="unique_member_no_per_isolated_member_registry",
            )
        ]

    @property
    def name(self):
        return localized(self.name_ne, self.name_en or self.name_ne)

    def save(self, *args, **kwargs):
        if self.membership_number:
            self.membership_number_int = membership_number_as_int(self.membership_number)

        if not self.membership_number and self.level and self.unit_name and self.membership_type:
            highest_no = (
                Member.objects.filter(
                    level=self.level,
                    unit_name=self.unit_name,
                    membership_type=self.membership_type,
                )
                .exclude(pk=self.pk)
                .aggregate(max_no=Max("membership_number_int"))["max_no"]
                or 0
            )
            self.membership_number_int = highest_no + 1
            self.membership_number = str(self.membership_number_int)

        super().save(*args, **kwargs)

    def __str__(self):
        number = f" #{self.membership_number}" if self.membership_number else ""
        unit = f" - {self.unit_name}" if self.unit_name else ""
        return f"{self.name_en or self.name_ne}{number}{unit}"


class Person(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name_ne = models.CharField(max_length=180, verbose_name=_("Name (Nepali)"))
    name_en = models.CharField(max_length=180, blank=True, verbose_name=_("Name (English)"))
    normalized_name = models.CharField(max_length=220, blank=True, editable=False, db_index=True)
    phone = models.CharField(
        max_length=24,
        blank=True,
        verbose_name=_("Private phone number"),
        help_text=_("Never shown in the public member directory."),
    )
    email = models.EmailField(blank=True, verbose_name=_("Private email address"))
    location = models.CharField(max_length=255, blank=True)
    is_public = models.BooleanField(default=True)
    needs_identity_review = models.BooleanField(default=False)
    merged_into = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="merged_people",
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name_ne", "name_en"]
        verbose_name = _("Person")
        verbose_name_plural = _("People")
        indexes = [
            models.Index(fields=["is_public", "normalized_name"]),
            models.Index(fields=["phone"]),
        ]

    @property
    def display_name(self):
        return localized(self.name_ne, self.name_en or self.name_ne)

    def save(self, *args, **kwargs):
        self.normalized_name = normalize_person_name(self.name_ne or self.name_en)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_en or self.name_ne


class MembershipCategory(models.Model):
    code = models.SlugField(max_length=40, unique=True)
    name_ne = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name_en"]
        verbose_name = _("Membership category")
        verbose_name_plural = _("Membership categories")

    @property
    def name(self):
        return localized(self.name_ne, self.name_en)

    def __str__(self):
        return self.name_en


class OrganizationUnit(models.Model):
    LEVEL_CHOICES = Member.LEVEL_CHOICES + [("other", _("Other"))]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    level = models.CharField(max_length=30, choices=LEVEL_CHOICES, default="unknown")
    name_ne = models.CharField(max_length=180, blank=True)
    name_en = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    geographic_name = models.CharField(max_length=180, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "level", "name_en"]
        verbose_name = _("Organization unit")
        verbose_name_plural = _("Organization units")
        constraints = [
            models.UniqueConstraint(
                fields=["level", "name_en"],
                name="unique_organization_unit_level_name",
            )
        ]

    @property
    def name(self):
        return localized(self.name_ne or self.name_en, self.name_en)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name_en) or f"unit-{uuid.uuid4().hex[:8]}"
            slug = base
            counter = 2
            while OrganizationUnit.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_en


class ImportBatch(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("dry_run", _("Dry run")),
        ("completed", _("Completed")),
        ("failed", _("Failed")),
        ("rolled_back", _("Rolled back")),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    source_file_name = models.CharField(max_length=255)
    source_checksum = models.CharField(max_length=64, db_index=True)
    source_sheet = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_dry_run = models.BooleanField(default=False)
    options = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="member_import_batches",
    )

    class Meta:
        ordering = ["-started_at"]
        verbose_name = _("Member import batch")
        verbose_name_plural = _("Member import batches")
        indexes = [models.Index(fields=["source_checksum", "status"])]

    def __str__(self):
        return f"{self.source_file_name} — {self.started_at:%Y-%m-%d %H:%M}"


class MembershipRecord(models.Model):
    STATUS_CHOICES = [
        ("active", _("Active")),
        ("expired", _("Expired")),
        ("unknown", _("Unknown")),
        ("archived", _("Archived")),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="memberships")
    category = models.ForeignKey(
        MembershipCategory,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    organization_unit = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    membership_number = models.CharField(max_length=60, blank=True)
    membership_number_normalized = models.CharField(
        max_length=60,
        blank=True,
        editable=False,
        db_index=True,
    )
    membership_number_int = models.PositiveIntegerField(null=True, blank=True, editable=False)
    source_identity_key = models.CharField(max_length=160, blank=True, db_index=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unknown")
    joined_date = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=180, blank=True)
    destination_country = models.CharField(max_length=150, blank=True)
    address_display = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("General locality only; do not enter a private street address."),
    )
    is_public = models.BooleanField(default=True)
    legacy_member = models.OneToOneField(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="normalized_membership",
    )
    source_application = models.OneToOneField(
        "core.Membership",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="normalized_membership",
    )
    created_by_import = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_memberships",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "organization_unit__display_order",
            "organization_unit__name_en",
            "category__display_order",
            "membership_number_int",
            "membership_number_normalized",
        ]
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        indexes = [
            models.Index(fields=["person", "status", "is_public"]),
            models.Index(fields=["category", "organization_unit"]),
            models.Index(fields=["organization_unit", "membership_number_int"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization_unit", "source_identity_key"],
                condition=~Q(source_identity_key=""),
                name="unique_membership_source_identity_per_unit",
            ),
        ]

    def clean(self):
        if not self.category_id:
            raise ValidationError({"category": _("Membership category is required.")})
        if not self.organization_unit_id:
            raise ValidationError({"organization_unit": _("Organization unit is required.")})

    def save(self, *args, **kwargs):
        self.membership_number = str(self.membership_number or "").strip()
        self.membership_number_normalized = normalize_membership_number(self.membership_number)
        self.membership_number_int = membership_number_as_int(self.membership_number)
        super().save(*args, **kwargs)

    def __str__(self):
        number = f" #{self.membership_number}" if self.membership_number else ""
        return f"{self.person} — {self.category}{number}"


class ImportRowRecord(models.Model):
    STATUS_CHOICES = [
        ("imported", _("Imported")),
        ("updated", _("Updated")),
        ("unchanged", _("Unchanged")),
        ("duplicate", _("Potential duplicate")),
        ("warning", _("Imported with warnings")),
        ("failed", _("Failed")),
        ("skipped", _("Non-data row")),
    ]

    batch = models.ForeignKey(ImportBatch, on_delete=models.PROTECT, related_name="rows")
    row_number = models.PositiveIntegerField()
    row_checksum = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    original_data = models.JSONField(default=dict)
    normalized_data = models.JSONField(default=dict)
    warnings = models.JSONField(default=list, blank=True)
    error_message = models.TextField(blank=True)
    person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_rows",
    )
    membership = models.ForeignKey(
        MembershipRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_rows",
    )
    created_person = models.BooleanField(default=False)
    created_membership = models.BooleanField(default=False)
    before_person = models.JSONField(default=dict, blank=True)
    before_membership = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["batch", "row_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "row_number"],
                name="unique_import_row_number_per_batch",
            )
        ]

    def __str__(self):
        return f"{self.batch.source_file_name} row {self.row_number}: {self.status}"


class PotentialDuplicate(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Pending review")),
        ("same", _("Confirmed same person")),
        ("different", _("Confirmed different people")),
        ("dismissed", _("Dismissed")),
    ]

    person_a = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="duplicate_as_a")
    person_b = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="duplicate_as_b")
    signals = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["person_a", "person_b"],
                name="unique_potential_duplicate_pair",
            ),
            models.CheckConstraint(
                condition=~Q(person_a=models.F("person_b")),
                name="potential_duplicate_people_must_differ",
            ),
        ]

    def clean(self):
        if self.person_a_id and self.person_b_id and self.person_a_id > self.person_b_id:
            self.person_a_id, self.person_b_id = self.person_b_id, self.person_a_id

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.person_a} ↔ {self.person_b}"
