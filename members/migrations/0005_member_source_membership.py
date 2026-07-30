from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_membership_email"),
        ("members", "0004_remove_member_unique_member_no_per_isolated_member_registry_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="source_membership",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="member_record",
                to="core.membership",
                verbose_name="Source membership application",
            ),
        ),
    ]
