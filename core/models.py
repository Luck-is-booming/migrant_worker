# blog/models.py
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _

class OrganizationInfo(models.Model):
    """Bilingual structural core data variables for the administrative portal context."""
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

    class Meta:
        verbose_name = _("Organization Information")
        verbose_name_plural = _("Organization Information")

    # --- LANDING PAGE TEMPLATE INTEGRATION PROPERTIES ---
    @property
    def name(self):
        return self.name_ne if get_language() == 'ne' else self.name_en

    @property
    def slogan(self):
        return self.slogan_ne if get_language() == 'ne' else self.slogan_en

    @property
    def objective(self):
        return self.objective_ne if get_language() == 'ne' else self.objective_en

    @property
    def commitment(self):
        return self.commitment_ne if get_language() == 'ne' else self.commitment_en

    @property
    def chairperson(self):
        return self.chairperson_name_ne if get_language() == 'ne' else self.chairperson_name_en

    @property
    def message(self):
        return self.chairperson_message_ne if get_language() == 'ne' else self.chairperson_message_en

    def __str__(self):
        return self.name_en


class ServiceCard(models.Model):
    """Dynamic operational service vectors showcasing core support features."""
    icon_svg = models.TextField(
        help_text=_("Paste raw HTML/SVG icon code here."), 
        verbose_name=_("Raw SVG Icon Code")
    )
    title_ne = models.CharField(max_length=255, verbose_name=_("Title (Nepali)"))
    title_en = models.CharField(max_length=255, verbose_name=_("Title (English)"))
    desc_ne = models.TextField(verbose_name=_("Description (Nepali)"))
    desc_en = models.TextField(verbose_name=_("Description (English)"))
    process_ne = models.TextField(verbose_name=_("Process Steps (Nepali)"), default="सम्बन्धित कागजात सहित केन्द्रमा सम्पर्क राख्ने।")
    process_en = models.TextField(verbose_name=_("Process Steps (English)"), default="Contact the center with all necessary documentation.")

    # --- LANDING PAGE TEMPLATE INTEGRATION PROPERTIES ---
    @property
    def title(self):
        return self.title_ne if get_language() == 'ne' else self.title_en

    @property
    def desc(self):
        return self.desc_ne if get_language() == 'ne' else self.desc_en

    @property
    def process(self):
        return self.process_ne if get_language() == 'ne' else self.process_en

    @property
    def icon(self):
        return self.icon_svg

    def __str__(self):
        return self.title_en


class DestinationCountry(models.Model):
    """Destination profile dataset mapping labor structures, wages, and emergency tracking."""
    name_ne = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    flag_emoji = models.CharField(max_length=10, default="🌐")
    min_wage_ne = models.CharField(max_length=100, default="रु ४५,०००")
    min_wage_en = models.CharField(max_length=100, default="NPR 45,000 equivalent")
    laws_summary_ne = models.TextField()
    laws_summary_en = models.TextField()
    embassy_contact_ne = models.TextField()
    embassy_contact_en = models.TextField()

    @property
    def name(self):
        return self.name_ne if get_language() == 'ne' else self.name_en

    @property
    def min_wage(self):
        return self.min_wage_ne if get_language() == 'ne' else self.min_wage_en

    def __str__(self):
        return self.name_en


class ResourcePublication(models.Model):
    """Digital directory structures for technical research papers or guidelines sheets."""
    title_ne = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    file_size = models.CharField(max_length=50, default="2.4 MB")
    download_url = models.CharField(max_length=500, default="#")

    @property
    def title(self):
        return self.title_ne if get_language() == 'ne' else self.title_en

    def __str__(self):
        return self.title_en


class ContactMessage(models.Model):
    """Public inquiries database logging tracking entries securely."""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class TeamMember(models.Model):
    name = models.CharField(max_length=150, verbose_name="Full Name")
    designation = models.CharField(max_length=100, verbose_name="Official Designation")
    email = models.EmailField(blank=True, null=True, verbose_name="Official Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Extension / Phone")
    image = models.ImageField(upload_to='team_photos/', blank=True, null=True, verbose_name="Profile Photo")
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower numbers display first.")
    is_active = models.BooleanField(default=True, verbose_name="Show on Website")

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.designation}"    