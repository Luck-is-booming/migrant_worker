from django.db import migrations, models
from django.db.models import Q


def normalize(value):
    return "".join(str(value or "").split()).casefold()


def backfill(apps, schema_editor):
    ManualPayment = apps.get_model("payments", "ManualPayment")
    seen = set()
    for payment in ManualPayment.objects.order_by("pk").iterator():
        normalized = normalize(payment.transaction_id)
        if normalized in seen:
            normalized = ""
        elif normalized:
            seen.add(normalized)
        payment.transaction_id_normalized = normalized
        payment.save(update_fields=["transaction_id_normalized"])


class Migration(migrations.Migration):
    dependencies = [("payments", "0003_randomize_private_evidence_paths")]

    operations = [
        migrations.AddField(
            model_name="manualpayment",
            name="rejection_reason",
            field=models.TextField(blank=True, help_text="Required before rejection. Write a clear reason safe to show to the applicant.", max_length=1000, verbose_name="Applicant-facing rejection reason"),
        ),
        migrations.AlterField(
            model_name="manualpayment",
            name="admin_note",
            field=models.TextField(blank=True, help_text="Internal staff note. This is not shown to the applicant.", max_length=2000),
        ),
        migrations.AddField(
            model_name="manualpayment",
            name="transaction_id_normalized",
            field=models.CharField(blank=True, db_index=True, editable=False, max_length=120),
        ),
        migrations.RunPython(backfill, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="manualpayment",
            constraint=models.UniqueConstraint(
                condition=~Q(transaction_id_normalized=""),
                fields=("transaction_id_normalized",),
                name="unique_nonblank_payment_transaction_reference",
            ),
        ),
    ]
