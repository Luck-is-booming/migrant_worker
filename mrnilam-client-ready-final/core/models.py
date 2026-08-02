from django.core.validators import URLValidator
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from .i18n_utils import localized


class OrganizationInfo(models.Model):
    name_ne = models.CharField(max_length=255, verbose_name=_("Name (Nepali)"))
    name_en = models.CharField(max_length=255, verbose_name=_("Name (English)"))
    slogan_ne = models.CharField(max_length=500, verbose_name=_("Slogan (Nepali)"))
    slogan_en = models.CharField(max_length=500, verbose_name=_("Slogan (English)"))
    objective_ne = models.TextField(verbose_name=_("Objective (Nepali)"))
    objective_en = models.TextField(verbose_name=_("Objective (English)"))
    commitment_ne = models.TextField(verbose_name=_("Commitment (Nepali)"))
    commitment_en = models.TextField(verbose_name=_("Commitment (English)"))
    chairperson_name_ne = models.CharField(max_length=255, blank=True)
    chairperson_name_en = models.CharField(max_length=255, blank=True)
    chairperson_message_ne = models.TextField(blank=True)
    chairperson_message_en = models.TextField(blank=True)
    chairperson_photo = models.ImageField(
        upload_to="chairperson_photos/",
        blank=True,
        null=True,
        verbose_name=_("Chairperson Photo"),
    )
    registration_number = models.CharField(max_length=120, blank=True)
    registration_authority_ne = models.CharField(max_length=255, blank=True)
    registration_authority_en = models.CharField(max_length=255, blank=True)
    established_date = models.DateField(null=True, blank=True)
    service_area_ne = models.CharField(max_length=255, blank=True)
    service_area_en = models.CharField(max_length=255, blank=True)
    official_phone = models.CharField(max_length=30, blank=True)
    official_email = models.EmailField(blank=True)
    office_address_ne = models.CharField(max_length=255, blank=True)
    office_address_en = models.CharField(max_length=255, blank=True)
    service_hours_ne = models.CharField(max_length=255, blank=True)
    service_hours_en = models.CharField(max_length=255, blank=True)
    disclaimer_ne = models.TextField(
        default=(
            "हामी वैदेशिक रोजगारसम्बन्धी सूचना, सचेतना र परामर्श प्रदान गर्छौं। "
            "हामी भिसा जारी गर्दैनौं, रोजगारीको ग्यारेन्टी गर्दैनौं र भर्ती एजेन्सी होइनौं।"
        )
    )
    disclaimer_en = models.TextField(
        default=(
            "We provide information, awareness, and counseling related to foreign employment. "
            "We do not issue visas, guarantee employment, or operate as a recruitment agency."
        )
    )

    class Meta:
        verbose_name = _("Organization Information")
        verbose_name_plural = _("Organization Information")

    @property
    def name(self):
        return localized(self.name_ne, self.name_en)

    @property
    def slogan(self):
        return localized(self.slogan_ne, self.slogan_en)

    @property
    def objective(self):
        return localized(self.objective_ne, self.objective_en)

    @property
    def commitment(self):
        return localized(self.commitment_ne, self.commitment_en)

    @property
    def chairperson(self):
        return localized(self.chairperson_name_ne, self.chairperson_name_en)

    @property
    def message(self):
        return localized(self.chairperson_message_ne, self.chairperson_message_en)

    @property
    def registration_authority(self):
        return localized(self.registration_authority_ne, self.registration_authority_en)

    @property
    def service_area(self):
        return localized(self.service_area_ne, self.service_area_en)

    @property
    def office_address(self):
        return localized(self.office_address_ne, self.office_address_en)

    @property
    def service_hours(self):
        return localized(self.service_hours_ne, self.service_hours_en)

    @property
    def disclaimer(self):
        return localized(self.disclaimer_ne, self.disclaimer_en)

    def __str__(self):
        return self.name_en


class MembershipPaymentSettings(models.Model):
    """Administrator-managed official membership payment configuration."""

    singleton_key = models.PositiveSmallIntegerField(
        default=1, unique=True, editable=False
    )
    general_member_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("General Membership fee")
    )
    life_member_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Life Membership fee")
    )
    recipient_name = models.CharField(
        max_length=180, blank=True, verbose_name=_("Official payment recipient name")
    )
    payment_qr = models.ImageField(
        upload_to="membership_payment/",
        blank=True,
        null=True,
        verbose_name=_("Official payment QR image"),
        help_text=_(
            "Upload only the QR confirmed by the organization. Verify the recipient "
            "name by scanning it before publishing."
        ),
    )
    account_details_ne = models.TextField(blank=True, verbose_name=_("Payment account details (Nepali)"))
    account_details_en = models.TextField(blank=True, verbose_name=_("Payment account details (English)"))
    instructions_ne = models.TextField(blank=True, verbose_name=_("Payment instructions (Nepali)"))
    instructions_en = models.TextField(blank=True, verbose_name=_("Payment instructions (English)"))
    is_active = models.BooleanField(
        default=False,
        help_text=_(
            "Enable only after the QR, recipient name, and official fees have been verified."
        ),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Membership payment settings")
        verbose_name_plural = _("Membership payment settings")

    @property
    def account_details(self):
        return localized(self.account_details_ne, self.account_details_en)

    @property
    def instructions(self):
        return localized(self.instructions_ne, self.instructions_en)

    def amount_for(self, membership_type):
        return self.life_member_amount if membership_type == "life" else self.general_member_amount

    @property
    def is_ready(self):
        return bool(
            self.is_active
            and self.payment_qr
            and self.recipient_name.strip()
            and self.general_member_amount > 0
            and self.life_member_amount > 0
        )

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.is_active:
            if self.general_member_amount <= 0:
                errors["general_member_amount"] = _("Enter the verified General Membership fee.")
            if self.life_member_amount <= 0:
                errors["life_member_amount"] = _("Enter the verified Life Membership fee.")
            if not self.recipient_name.strip():
                errors["recipient_name"] = _("Enter the verified payment recipient name.")
            if not self.payment_qr:
                errors["payment_qr"] = _("Upload the verified official payment QR image.")
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Create or update the single payment configuration row.

        ``QuerySet.create()`` passes ``force_insert=True``. When the singleton
        already exists, reuse that row and switch to a normal update so an
        accidental second create cannot produce another configuration or fail
        unique validation.
        """
        self.singleton_key = 1
        existing_pk = type(self).objects.filter(singleton_key=1).values_list(
            "pk", flat=True
        ).first()
        if self._state.adding and existing_pk:
            self.pk = existing_pk
            self._state.adding = False
            kwargs.pop("force_insert", None)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(_("Membership payment settings"))


class ServiceCard(models.Model):
    ICON_CHOICES = [
        ("guidance", _("Guidance")),
        ("shield", _("Safety")),
        ("document", _("Documents")),
        ("rights", _("Rights")),
        ("family", _("Family")),
        ("return", _("Return")),
    ]

    icon_svg = models.TextField(
        blank=True,
        help_text=_("Legacy field. Raw SVG is no longer rendered publicly."),
        verbose_name=_("Legacy raw SVG"),
    )
    icon_name = models.CharField(max_length=30, choices=ICON_CHOICES, default="guidance")
    title_ne = models.CharField(max_length=255, verbose_name=_("Title (Nepali)"))
    title_en = models.CharField(max_length=255, verbose_name=_("Title (English)"))
    desc_ne = models.TextField(verbose_name=_("Description (Nepali)"))
    desc_en = models.TextField(verbose_name=_("Description (English)"))
    process_ne = models.TextField(verbose_name=_("Process Steps (Nepali)"), blank=True)
    process_en = models.TextField(verbose_name=_("Process Steps (English)"), blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]

    @property
    def title(self):
        return localized(self.title_ne, self.title_en)

    @property
    def desc(self):
        return localized(self.desc_ne, self.desc_en)

    @property
    def process(self):
        return localized(self.process_ne, self.process_en)

    @property
    def icon(self):
        return self.icon_name

    def __str__(self):
        return self.title_en


class DestinationCountry(models.Model):
    name_ne = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    flag_emoji = models.CharField(max_length=10, default="🌐")
    min_wage_ne = models.CharField(max_length=100, blank=True)
    min_wage_en = models.CharField(max_length=100, blank=True)
    laws_summary_ne = models.TextField(blank=True)
    laws_summary_en = models.TextField(blank=True)
    embassy_contact_ne = models.TextField(blank=True)
    embassy_contact_en = models.TextField(blank=True)
    estimated_cost = models.PositiveIntegerField(
        default=0,
        help_text=_("Informational estimate only. Set to zero when unverified."),
    )
    last_reviewed = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name_en"]

    @property
    def name(self):
        return localized(self.name_ne, self.name_en)

    @property
    def min_wage(self):
        return localized(self.min_wage_ne, self.min_wage_en)

    @property
    def cost(self):
        return self.estimated_cost

    @property
    def flag(self):
        return self.flag_emoji

    def __str__(self):
        return self.name_en


class ResourcePublication(models.Model):
    """Legacy resource link retained while records move to OfficialResource."""

    title_ne = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    file_size = models.CharField(max_length=50, blank=True)
    download_url = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Legacy resource publication")

    @property
    def title(self):
        return localized(self.title_ne, self.title_en)

    @property
    def file_url(self):
        return self.download_url or "#"

    @property
    def size(self):
        return self.file_size

    @property
    def category(self):
        return localized("निर्देशिका र पुस्तिकाहरू", "Guides & Manuals")

    def __str__(self):
        return self.title_en


class ResourceCategory(models.Model):
    name_ne = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name_en"]
        verbose_name_plural = "Resource categories"

    @property
    def name(self):
        return localized(self.name_ne, self.name_en)

    def __str__(self):
        return self.name_en


class OfficialResource(models.Model):
    LANGUAGE_CHOICES = [("both", _("Both languages")), ("ne", _("Nepali")), ("en", _("English"))]

    category = models.ForeignKey(ResourceCategory, on_delete=models.PROTECT, related_name="resources")
    title_ne = models.CharField(max_length=255, blank=True)
    title_en = models.CharField(max_length=255, blank=True)
    description_ne = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    url = models.URLField(max_length=600, validators=[URLValidator(schemes=["https"])])
    is_official_source = models.BooleanField(default=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="both")
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    last_reviewed = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["category__display_order", "display_order", "title_en"]
        indexes = [models.Index(fields=["is_active", "category", "display_order"])]

    @property
    def title(self):
        return localized(self.title_ne, self.title_en)

    @property
    def description(self):
        return localized(self.description_ne, self.description_en)

    def __str__(self):
        return self.title_en or self.title_ne


class EmergencyResource(models.Model):
    title_ne = models.CharField(max_length=180)
    title_en = models.CharField(max_length=180)
    guidance_ne = models.TextField(blank=True)
    guidance_en = models.TextField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    url = models.URLField(max_length=600, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    last_reviewed = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["display_order", "title_en"]

    @property
    def title(self):
        return localized(self.title_ne, self.title_en)

    @property
    def guidance(self):
        return localized(self.guidance_ne, self.guidance_en)

    def __str__(self):
        return self.title_en


class FrequentlyAskedQuestion(models.Model):
    question_ne = models.CharField(max_length=300)
    question_en = models.CharField(max_length=300)
    answer_ne = models.TextField()
    answer_en = models.TextField()
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]

    @property
    def question(self):
        return localized(self.question_ne, self.question_en)

    @property
    def answer(self):
        return localized(self.answer_ne, self.answer_en)

    def __str__(self):
        return self.question_en


class ContactMessage(models.Model):
    STATUS_CHOICES = [("new", _("New")), ("reviewed", _("Reviewed")), ("closed", _("Closed")), ("spam", _("Spam"))]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=24)
    email = models.EmailField(blank=True)
    preferred_language = models.CharField(max_length=10, choices=[("ne", _("Nepali")), ("en", _("English")), ("either", _("Either"))], default="ne")
    subject = models.CharField(max_length=255)
    message = models.TextField(max_length=5000)
    consent_to_contact = models.BooleanField(default=False)
    consent_recorded_at = models.DateTimeField(auto_now_add=True)
    source_ip_hash = models.CharField(max_length=64, blank=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


class TeamMember(models.Model):
    name_ne = models.CharField(max_length=180, verbose_name=_("Name (Nepali)"))
    name_en = models.CharField(max_length=180, blank=True, verbose_name=_("Name (English)"))
    designation_ne = models.CharField(
        max_length=180, verbose_name=_("Designation (Nepali)")
    )
    designation_en = models.CharField(
        max_length=180, blank=True, verbose_name=_("Designation (English)")
    )
    address_ne = models.CharField(
        max_length=255, blank=True, verbose_name=_("Address (Nepali)")
    )
    address_en = models.CharField(
        max_length=255, blank=True, verbose_name=_("Address (English)")
    )
    email = models.EmailField(blank=True, null=True, verbose_name=_("Official Email"))
    phone = models.CharField(
        max_length=24, blank=True, null=True, verbose_name=_("Extension / Phone")
    )
    image = models.ImageField(
        upload_to="team_photos/", blank=True, null=True, verbose_name=_("Profile Photo")
    )
    sort_order = models.PositiveIntegerField(
        default=0, help_text=_("Lower numbers display first.")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Show on Website"))

    class Meta:
        ordering = ["sort_order", "name_en", "name_ne"]
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")

    @property
    def name(self):
        return localized(self.name_ne, self.name_en or self.name_ne)

    @property
    def designation(self):
        return localized(self.designation_ne, self.designation_en)

    @property
    def address(self):
        return localized(self.address_ne, self.address_en)

    @property
    def translation_complete(self):
        return bool(self.name_ne and self.name_en and self.designation_ne and self.designation_en)

    def __str__(self):
        return f"{self.name_en or self.name_ne} - {self.designation_en or self.designation_ne}"


class Membership(models.Model):
    """Online membership application; not the official membership registry."""

    MUNICIPALITY_CHOICES = [
        ("ilam", _("Ilam Municipality")),
        ("deumai", _("Deumai Municipality")),
        ("suryodaya", _("Suryodaya Municipality")),
        ("phakphokthum", _("Phakphokthum Rural Municipality")),
        ("sandakpur", _("Sandakpur Rural Municipality")),
    ]
    TYPE_CHOICES = [("life", _("Life Member")), ("general", _("General Member"))]
    PAYMENT_STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("completed", _("Completed")),
        ("rejected", _("Rejected")),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=180)
    name_en = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, verbose_name=_("Email address"))
    municipality = models.CharField(max_length=50, choices=MUNICIPALITY_CHOICES)
    ward_no = models.PositiveSmallIntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=150, blank=True)
    destination_country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=24)
    membership_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    consent_to_privacy = models.BooleanField(default=False)
    consent_recorded_at = models.DateTimeField(auto_now_add=True)
    source_ip_hash = models.CharField(max_length=64, blank=True, editable=False)
    joined_date = models.DateField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        ordering = ["-joined_date"]
        verbose_name = _("Membership application")
        verbose_name_plural = _("Membership applications")

    def __str__(self):
        return f"{self.name} - {self.get_membership_type_display()}"
