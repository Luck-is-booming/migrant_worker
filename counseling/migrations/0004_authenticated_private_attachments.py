import core.storage
import counseling.models
import counseling.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("counseling", "0003_randomize_private_attachment_paths")]

    operations = [
        migrations.AlterField(
            model_name="counselingrequest",
            name="attachment",
            field=models.FileField(
                blank=True,
                storage=core.storage.get_private_media_storage,
                upload_to=counseling.models.private_counseling_attachment_path,
                validators=[counseling.validators.validate_private_attachment],
            ),
        ),
    ]
