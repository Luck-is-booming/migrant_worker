import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(model_name="manualpayment", name="public_id", field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
        migrations.AlterField(model_name="manualpayment", name="membership", field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="manual_payments", to="core.membership")),
        migrations.AlterField(model_name="manualpayment", name="screenshot", field=models.ImageField(upload_to="private/payment_proofs/%Y/%m/", verbose_name="Payment Screenshot")),
        migrations.AlterField(model_name="manualpayment", name="note", field=models.TextField(blank=True, max_length=2000)),
        migrations.AlterField(model_name="manualpayment", name="admin_note", field=models.TextField(blank=True, max_length=2000)),
        migrations.AlterField(model_name="manualpayment", name="status", field=models.CharField(choices=[("pending", "Pending"), ("needs_review", "Needs review"), ("approved", "Approved"), ("rejected", "Rejected")], db_index=True, default="pending", max_length=20)),
        migrations.AlterField(model_name="manualpayment", name="reviewed_by", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_manual_payments", to=settings.AUTH_USER_MODEL)),
        migrations.AddIndex(model_name="manualpayment", index=models.Index(fields=["status", "-submitted_at"], name="payments_ma_status_0321a0_idx")),
        migrations.AddConstraint(model_name="manualpayment", constraint=models.UniqueConstraint(condition=Q(status__in=["pending", "needs_review", "approved"]), fields=("membership",), name="one_open_or_approved_payment_per_application")),
        migrations.CreateModel(
            name="PaymentReviewEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("old_status", models.CharField(blank=True, max_length=20)),
                ("new_status", models.CharField(max_length=20)),
                ("note", models.TextField(blank=True, max_length=2000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("changed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("payment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="review_events", to="payments.manualpayment")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
