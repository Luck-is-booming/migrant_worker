import core.storage
import payments.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("payments", "0004_transaction_reference_integrity")]

    operations = [
        migrations.AlterField(
            model_name="manualpayment",
            name="screenshot",
            field=models.ImageField(
                storage=core.storage.get_private_media_storage,
                upload_to=payments.models.private_payment_evidence_path,
                verbose_name="Payment Screenshot",
            ),
        ),
    ]
