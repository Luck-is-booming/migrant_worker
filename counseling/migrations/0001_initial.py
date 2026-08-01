import uuid

import counseling.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


CATEGORIES = [
    ("process", "वैदेशिक रोजगार प्रक्रिया बुझ्ने", "Understanding the foreign-employment process", 1),
    ("suspicious-offer", "शंकास्पद प्रस्ताव जाँच", "Checking whether an offer appears suspicious", 2),
    ("recruitment-fees", "भर्ती शुल्कसम्बन्धी चिन्ता", "Recruitment-fee concerns", 3),
    ("contract", "करारसम्बन्धी प्रश्न", "Contract questions", 4),
    ("pre-departure", "प्रस्थानपूर्व तयारी", "Pre-departure preparation", 5),
    ("documents", "कागजात सचेतना", "Documentation awareness", 6),
    ("labor-approval", "श्रम स्वीकृति सचेतना", "Labor approval awareness", 7),
    ("insurance-welfare", "बीमा तथा कल्याण सचेतना", "Insurance and welfare awareness", 8),
    ("workplace-rights", "कार्यस्थल अधिकार", "Workplace rights", 9),
    ("salary-dispute", "तलब वा करार विवाद", "Salary or contract disputes", 10),
    ("fraud", "ठगी वा जालसाजीको चिन्ता", "Fraud or scam concerns", 11),
    ("abroad-problem", "विदेशमा परेको समस्या", "Problems faced abroad", 12),
    ("return-reintegration", "फिर्ती तथा पुनःएकीकरण", "Return and reintegration guidance", 13),
    ("family", "परिवार परामर्श", "Family guidance", 14),
    ("other", "अन्य", "Other", 99),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("counseling", "CounselingCategory")
    for code, name_ne, name_en, order in CATEGORIES:
        Category.objects.get_or_create(
            code=code,
            defaults={"name_ne": name_ne, "name_en": name_en, "display_order": order},
        )


def unseed_categories(apps, schema_editor):
    # Preserve staff-edited categories and any linked counseling history when
    # rolling application code backward. A reverse migration must not delete
    # operational records.
    pass


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="CounselingCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=80, unique=True)),
                ("name_ne", models.CharField(max_length=180)),
                ("name_en", models.CharField(max_length=180)),
                ("description_ne", models.TextField(blank=True)),
                ("description_en", models.TextField(blank=True)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["display_order", "name_en"], "verbose_name": "Counseling category", "verbose_name_plural": "Counseling categories"},
        ),
        migrations.CreateModel(
            name="CounselingRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("full_name", models.CharField(max_length=180)),
                ("phone", models.CharField(max_length=24)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("preferred_language", models.CharField(choices=[("ne", "Nepali"), ("en", "English"), ("either", "Either")], default="ne", max_length=10)),
                ("location", models.CharField(max_length=180)),
                ("message", models.TextField(max_length=5000)),
                ("preferred_contact_method", models.CharField(choices=[("phone", "Phone call"), ("sms", "SMS"), ("email", "Email"), ("whatsapp", "WhatsApp")], default="phone", max_length=20)),
                ("availability", models.CharField(blank=True, max_length=180)),
                ("attachment", models.FileField(blank=True, upload_to="private/counseling/%Y/%m/", validators=[counseling.validators.validate_private_attachment])),
                ("consent_to_contact", models.BooleanField(default=False)),
                ("consent_recorded_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("new", "New"), ("reviewed", "Reviewed"), ("contact_attempted", "Contact attempted"), ("in_counseling", "In counseling"), ("referred", "Referred"), ("resolved", "Resolved"), ("closed", "Closed"), ("spam", "Spam")], db_index=True, default="new", max_length=30)),
                ("internal_summary", models.CharField(blank=True, help_text="Staff-only short summary. Do not copy sensitive details into email.", max_length=500)),
                ("source_ip_hash", models.CharField(blank=True, editable=False, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_counseling_requests", to=settings.AUTH_USER_MODEL)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="requests", to="counseling.counselingcategory")),
            ],
            options={"ordering": ["-created_at"], "permissions": [("assign_counselingrequest", "Can assign counseling requests"), ("export_counselingrequest", "Can export counseling requests")]},
        ),
        migrations.CreateModel(
            name="CounselingNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("note", models.TextField(max_length=5000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ("request", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="notes", to="counseling.counselingrequest")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ContactAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("method", models.CharField(choices=[("phone", "Phone call"), ("sms", "SMS"), ("email", "Email"), ("whatsapp", "WhatsApp")], max_length=20)),
                ("outcome", models.CharField(choices=[("connected", "Connected"), ("no_answer", "No answer"), ("wrong_number", "Wrong number"), ("message_sent", "Message sent"), ("other", "Other")], max_length=30)),
                ("note", models.CharField(blank=True, max_length=500)),
                ("attempted_at", models.DateTimeField(auto_now_add=True)),
                ("attempted_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ("request", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="contact_attempts", to="counseling.counselingrequest")),
            ],
            options={"ordering": ["-attempted_at"]},
        ),
        migrations.AddIndex(model_name="counselingrequest", index=models.Index(fields=["status", "-created_at"], name="counseling__status_8a4ba4_idx")),
        migrations.AddIndex(model_name="counselingrequest", index=models.Index(fields=["assigned_to", "status"], name="counseling__assigned_85ea5d_idx")),
        migrations.RunPython(seed_categories, unseed_categories),
    ]
