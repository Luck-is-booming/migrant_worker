from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_client_ready_workflows"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contactmessage",
            name="consent_recorded_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="membership",
            name="consent_recorded_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
