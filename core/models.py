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
    chairperson_name_ne = models.CharField(max_length=255, default="राम बहादुर गुरुङ")
    chairperson_name_en = models.CharField(max_length=255, default="Ram Bahadur Gurung")
    chairperson_message_ne = models.TextField(default="सुरक्षित र मर्यादित वैदेशिक रोजगारी नै हाम्रो मुख्य लक्ष्य हो।")
    chairperson_message_en = models.TextField(default="Safe and dignified foreign employment is our primary mission.")
    chairperson_photo = models.ImageField(
    upload_to="chairperson_photos/",
    blank=True,
    null=True,
    verbose_name=_("Chairperson Photo"),
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

    def __str__(self):
        return self.name_en


class ServiceCard(models.Model):
    icon_svg = models.TextField(
        help_text=_("Paste raw HTML/SVG icon code here."),
        verbose_name=_("Raw SVG Icon Code"),
    )
    title_ne = models.CharField(max_length=255, verbose_name=_("Title (Nepali)"))
    title_en = models.CharField(max_length=255, verbose_name=_("Title (English)"))
    desc_ne = models.TextField(verbose_name=_("Description (Nepali)"))
    desc_en = models.TextField(verbose_name=_("Description (English)"))
    process_ne = models.TextField(
        verbose_name=_("Process Steps (Nepali)"),
        default="सम्बन्धित कागजात सहित केन्द्रमा सम्पर्क राख्ने।",
    )
    process_en = models.TextField(
        verbose_name=_("Process Steps (English)"),
        default="Contact the center with all necessary documentation.",
    )

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
        return self.icon_svg

    def __str__(self):
        return self.title_en


class DestinationCountry(models.Model):
    name_ne = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    flag_emoji = models.CharField(max_length=10, default="🌐")
    min_wage_ne = models.CharField(max_length=100, default="रु ४५,०००")
    min_wage_en = models.CharField(max_length=100, default="NPR 45,000 equivalent")
    laws_summary_ne = models.TextField()
    laws_summary_en = models.TextField()
    embassy_contact_ne = models.TextField()
    embassy_contact_en = models.TextField()
    estimated_cost = models.PositiveIntegerField(
        default=35000,
        help_text=_("Base deployment cost (NPR) used by the cost calculator."),
    )

    class Meta:
        ordering = ['name_en']

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
    title_ne = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    file_size = models.CharField(max_length=50, default="2.4 MB")
    download_url = models.CharField(max_length=500, default="#")

    class Meta:
        ordering = ['-id']

    @property
    def title(self):
        return localized(self.title_ne, self.title_en)

    @property
    def file_url(self):
        return self.download_url or "#"

    @property
    def size(self):
        return self.file_size or "1.2 MB"

    @property
    def category(self):
        return localized("निर्देशिका र पुस्तिकाहरू", "Guides & Manuals")

    def __str__(self):
        return self.title_en


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class TeamMember(models.Model):
    name = models.CharField(max_length=150, verbose_name="Full Name")
    designation = models.CharField(max_length=100, verbose_name="Official Designation")
    address = models.CharField(max_length=255, blank=True, verbose_name="Address")

    email = models.EmailField(blank=True, null=True, verbose_name="Official Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Extension / Phone")

    image = models.ImageField(
        upload_to="team_photos/",
        blank=True,
        null=True,
        verbose_name="Profile Photo"
    )

    sort_order = models.PositiveIntegerField(default=0, help_text="Lower numbers display first.")
    is_active = models.BooleanField(default=True, verbose_name="Show on Website")

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.designation}"

class Membership(models.Model):
    MUNICIPALITY_CHOICES = [
        ('ilam', _('Ilam Municipality')),
        ('deumai', _('Deumai Municipality')),
        ('suryodaya', _('Suryodaya Municipality')),
        ('phakphokthum', _('Phakphokthum Rural Municipality')),
        ('sandakpur', _('Sandakpur Rural Municipality')),
    ]

    TYPE_CHOICES = [
        ('life', _('Life Member')),
        ('general', _('General Member')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('completed', _('Completed')),
    ]

    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)

    municipality = models.CharField(max_length=50, choices=MUNICIPALITY_CHOICES)
    ward_no = models.PositiveSmallIntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)

    designation = models.CharField(max_length=150, blank=True)
    destination_country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    membership_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    joined_date = models.DateField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    # Keep this for admin/internal record, but don't ask normal users
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-joined_date']

    def __str__(self):
        return f"{self.name} - {self.payment_status}"
