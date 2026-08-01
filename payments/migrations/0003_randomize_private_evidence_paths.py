import payments.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("payments", "0002_payment_audit_and_privacy")]

    operations = [
        migrations.AlterField(
            model_name="manualpayment",
            name="screenshot",
            field=models.ImageField(
                upload_to=payments.models.private_payment_evidence_path,
                verbose_name="Payment Screenshot",
            ),
        ),
    ]
