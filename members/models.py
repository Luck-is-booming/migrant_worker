from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

from core.i18n_utils import localized


class Member(models.Model):
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
        help_text=_("Isolated inside Level + Unit + Membership Type. Example: District life no. 4 and Ilam Municipality life no. 1 can both exist."),
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

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Address"),
    )

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

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Phone Number"),
    )

    show_phone_publicly = models.BooleanField(
        default=False,
        verbose_name=_("Show Phone Publicly"),
    )

    is_public = models.BooleanField(
        default=True,
        verbose_name=_("Show on Website"),
    )

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
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
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
        condition=models.Q(membership_number_int__isnull=False),
        name="unique_member_no_per_isolated_member_registry",
    )
]

    @property
    def name(self):
        return localized(self.name_ne, self.name_en or self.name_ne)

    @staticmethod
    def _number_to_int(value):
        if value in (None, ""):
            return None
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return None

    def get_next_membership_number(self):
        highest_no = Member.objects.filter(
            level=self.level,
            unit_name=self.unit_name,
            membership_type=self.membership_type,
        ).exclude(pk=self.pk).aggregate(
            max_no=Max("membership_number_int")
        )["max_no"] or 0

        return highest_no + 1

    def save(self, *args, **kwargs):
        # If membership_number is manually filled, keep membership_number_int synced
        if self.membership_number:
            try:
                self.membership_number_int = int(str(self.membership_number).strip())
            except ValueError:
                self.membership_number_int = None

        # If membership_number is blank, auto-give the next number
        if not self.membership_number and self.level and self.unit_name and self.membership_type:
            highest_no = Member.objects.filter(
                level=self.level,
                unit_name=self.unit_name,
                membership_type=self.membership_type,
            ).exclude(pk=self.pk).aggregate(
                max_no=Max("membership_number_int")
            )["max_no"] or 0

            self.membership_number_int = highest_no + 1
            self.membership_number = str(self.membership_number_int)

        super().save(*args, **kwargs)

    def __str__(self):
        number = f" #{self.membership_number}" if self.membership_number else ""
        unit = f" - {self.unit_name}" if self.unit_name else ""
        return f"{self.name_en or self.name_ne}{number}{unit}"
