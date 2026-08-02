from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("counseling", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="counselingrequest",
            name="retention_status",
            field=models.CharField(
                choices=[
                    ("active", "Active retention"),
                    ("review_due", "Retention review due"),
                    ("retained", "Retained under policy"),
                    ("legal_hold", "Legal hold"),
                    ("anonymized", "Anonymized"),
                ],
                db_index=True,
                default="active",
                max_length=20,
            ),
        )
    ]
