import uuid

from django.db import migrations, models
from django.utils import timezone


def fill_membership_public_ids(apps, schema_editor):
    Membership = apps.get_model("core", "Membership")
    for row in Membership.objects.filter(public_id__isnull=True).iterator():
        row.public_id = uuid.uuid4()
        row.save(update_fields=["public_id"])


class Migration(migrations.Migration):
    dependencies = [("core", "0013_counseling_first_content")]

    operations = [
        migrations.AlterField(
            model_name="organizationinfo",
            name="chairperson_name_ne",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="organizationinfo",
            name="chairperson_name_en",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="organizationinfo",
            name="chairperson_message_ne",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="organizationinfo",
            name="chairperson_message_en",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="organizationinfo",
            name="registration_authority_ne",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="organizationinfo",
            name="registration_authority_en",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="organizationinfo",
            name="service_area_ne",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="organizationinfo",
            name="service_area_en",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RenameField(
            model_name="teammember",
            old_name="name",
            new_name="name_ne",
        ),
        migrations.RenameField(
            model_name="teammember",
            old_name="designation",
            new_name="designation_ne",
        ),
        migrations.RenameField(
            model_name="teammember",
            old_name="address",
            new_name="address_ne",
        ),
        migrations.AlterField(
            model_name="teammember",
            name="name_ne",
            field=models.CharField(max_length=180, verbose_name="Name (Nepali)"),
        ),
        migrations.AddField(
            model_name="teammember",
            name="name_en",
            field=models.CharField(blank=True, max_length=180, verbose_name="Name (English)"),
        ),
        migrations.AlterField(
            model_name="teammember",
            name="designation_ne",
            field=models.CharField(max_length=180, verbose_name="Designation (Nepali)"),
        ),
        migrations.AddField(
            model_name="teammember",
            name="designation_en",
            field=models.CharField(blank=True, max_length=180, verbose_name="Designation (English)"),
        ),
        migrations.AlterField(
            model_name="teammember",
            name="address_ne",
            field=models.CharField(blank=True, max_length=255, verbose_name="Address (Nepali)"),
        ),
        migrations.AddField(
            model_name="teammember",
            name="address_en",
            field=models.CharField(blank=True, max_length=255, verbose_name="Address (English)"),
        ),
        migrations.AlterField(
            model_name="teammember",
            name="phone",
            field=models.CharField(blank=True, max_length=24, null=True, verbose_name="Extension / Phone"),
        ),
        migrations.AlterModelOptions(
            name="teammember",
            options={
                "ordering": ["sort_order", "name_en", "name_ne"],
                "verbose_name": "Team Member",
                "verbose_name_plural": "Team Members",
            },
        ),
        migrations.AddField(
            model_name="contactmessage",
            name="consent_recorded_at",
            field=models.DateTimeField(default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="contactmessage",
            name="source_ip_hash",
            field=models.CharField(blank=True, editable=False, max_length=64),
        ),
        migrations.AddField(
            model_name="membership",
            name="public_id",
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.RunPython(fill_membership_public_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="membership",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name="membership",
            name="consent_to_privacy",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="membership",
            name="consent_recorded_at",
            field=models.DateTimeField(default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="membership",
            name="source_ip_hash",
            field=models.CharField(blank=True, editable=False, max_length=64),
        ),
        migrations.AlterField(
            model_name="membership",
            name="name",
            field=models.CharField(max_length=180),
        ),
        migrations.AlterField(
            model_name="membership",
            name="phone",
            field=models.CharField(max_length=24),
        ),
        migrations.AlterField(
            model_name="contactmessage",
            name="preferred_language",
            field=models.CharField(
                choices=[("ne", "Nepali"), ("en", "English"), ("either", "Either")],
                default="ne",
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name="MembershipPaymentSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("singleton_key", models.PositiveSmallIntegerField(default=1, editable=False, unique=True)),
                ("general_member_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="General Membership fee")),
                ("life_member_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Life Membership fee")),
                ("recipient_name", models.CharField(blank=True, max_length=180, verbose_name="Official payment recipient name")),
                ("payment_qr", models.ImageField(blank=True, help_text="Upload only the QR confirmed by the organization. Verify the recipient name by scanning it before publishing.", null=True, upload_to="membership_payment/", verbose_name="Official payment QR image")),
                ("account_details_ne", models.TextField(blank=True, verbose_name="Payment account details (Nepali)")),
                ("account_details_en", models.TextField(blank=True, verbose_name="Payment account details (English)")),
                ("instructions_ne", models.TextField(blank=True, verbose_name="Payment instructions (Nepali)")),
                ("instructions_en", models.TextField(blank=True, verbose_name="Payment instructions (English)")),
                ("is_active", models.BooleanField(default=False, help_text="Enable only after the QR, recipient name, and official fees have been verified.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Membership payment settings",
                "verbose_name_plural": "Membership payment settings",
            },
        ),
    ]
