import counseling.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("counseling", "0002_counselingrequest_retention_status")]

    operations = [
        migrations.AlterField(
            model_name="counselingrequest",
            name="attachment",
            field=models.FileField(
                blank=True,
                upload_to=counseling.models.private_counseling_attachment_path,
                validators=[counseling.models.validate_private_attachment],
            ),
        ),
    ]
