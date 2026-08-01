import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.i18n_utils import localized
from .validators import validate_private_attachment


def private_counseling_attachment_path(instance, filename):
    suffix = Path(filename).suffix.casefold()[:10]
    return f"private/counseling/{uuid.uuid4().hex}{suffix}"



class CounselingCategory(models.Model):
    code = models.SlugField(max_length=80, unique=True)
    name_ne = models.CharField(max_length=180)
    name_en = models.CharField(max_length=180)
    description_ne = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name_en"]
        verbose_name = _("Counseling category")
        verbose_name_plural = _("Counseling categories")

    @property
    def name(self):
        return localized(self.name_ne, self.name_en)

    def __str__(self):
        return self.name_en


class CounselingRequest(models.Model):
    STATUS_CHOICES = [
        ("new", _("New")),
        ("reviewed", _("Reviewed")),
        ("contact_attempted", _("Contact attempted")),
        ("in_counseling", _("In counseling")),
        ("referred", _("Referred")),
        ("resolved", _("Resolved")),
        ("closed", _("Closed")),
        ("spam", _("Spam")),
    ]
    LANGUAGE_CHOICES = [("ne", _("Nepali")), ("en", _("English")), ("either", _("Either"))]
    CONTACT_CHOICES = [
        ("phone", _("Phone call")),
        ("sms", _("SMS")),
        ("email", _("Email")),
        ("whatsapp", _("WhatsApp")),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    full_name = models.CharField(max_length=180)
    phone = models.CharField(max_length=24)
    email = models.EmailField(blank=True)
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="ne")
    location = models.CharField(max_length=180)
    category = models.ForeignKey(
        CounselingCategory,
        on_delete=models.PROTECT,
        related_name="requests",
    )
    message = models.TextField(max_length=5000)
    preferred_contact_method = models.CharField(max_length=20, choices=CONTACT_CHOICES, default="phone")
    availability = models.CharField(max_length=180, blank=True)
    attachment = models.FileField(
        upload_to=private_counseling_attachment_path,
        blank=True,
        validators=[validate_private_attachment],
    )
    consent_to_contact = models.BooleanField(default=False)
    consent_recorded_at = models.DateTimeField(auto_now_add=True)
    retention_status = models.CharField(
        max_length=20,
        choices=[
            ("active", _("Active retention")),
            ("review_due", _("Retention review due")),
            ("retained", _("Retained under policy")),
            ("legal_hold", _("Legal hold")),
            ("anonymized", _("Anonymized")),
        ],
        default="active",
        db_index=True,
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new", db_index=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_counseling_requests",
    )
    internal_summary = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Staff-only short summary. Do not copy sensitive details into email."),
    )
    source_ip_hash = models.CharField(max_length=64, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("assign_counselingrequest", "Can assign counseling requests"),
            ("export_counselingrequest", "Can export counseling requests"),
        ]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def __str__(self):
        return f"Request {self.public_id}"


class CounselingNote(models.Model):
    request = models.ForeignKey(CounselingRequest, on_delete=models.PROTECT, related_name="notes")
    note = models.TextField(max_length=5000)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note for {self.request.public_id}"


class ContactAttempt(models.Model):
    OUTCOME_CHOICES = [
        ("connected", _("Connected")),
        ("no_answer", _("No answer")),
        ("wrong_number", _("Wrong number")),
        ("message_sent", _("Message sent")),
        ("other", _("Other")),
    ]

    request = models.ForeignKey(CounselingRequest, on_delete=models.PROTECT, related_name="contact_attempts")
    method = models.CharField(max_length=20, choices=CounselingRequest.CONTACT_CHOICES)
    outcome = models.CharField(max_length=30, choices=OUTCOME_CHOICES)
    note = models.CharField(max_length=500, blank=True)
    attempted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"{self.get_method_display()} — {self.get_outcome_display()}"
