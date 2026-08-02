from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("members", "0006_normalized_membership_registry")]

    operations = [
        migrations.AlterModelOptions(
            name="membershiprecord",
            options={
                "ordering": [
                    "organization_unit__display_order",
                    "organization_unit__name_en",
                    "category__display_order",
                    "membership_number_int",
                    "membership_number_normalized",
                ],
                "verbose_name": "Membership",
                "verbose_name_plural": "Memberships",
            },
        ),
    ]
