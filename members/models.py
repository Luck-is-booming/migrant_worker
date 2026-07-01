from django.db import models
from django.utils.translation import gettext_lazy as _

from core.i18n_utils import localized


class Member(models.Model):
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
)

    municipality = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Municipality / Rural Municipality"),
    )

    ward_no = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Ward Number"),
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
        ordering = ["sort_order", "name_ne"]
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
        indexes = [
            models.Index(fields=["membership_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["municipality"]),
            models.Index(fields=["is_public"]),
        ]

    @property
    def name(self):
        return localized(self.name_ne, self.name_en or self.name_ne)

    def __str__(self):
        return self.name_en or self.name_ne