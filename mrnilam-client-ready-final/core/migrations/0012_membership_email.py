from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_organizationinfo_chairperson_photo_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="Email address"),
        ),
        migrations.AlterField(
            model_name="membership",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("completed", "Completed"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
