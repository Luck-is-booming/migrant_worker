from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_membership_amount_membership_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='destinationcountry',
            name='estimated_cost',
            field=models.PositiveIntegerField(
                default=35000,
                help_text='Base deployment cost (NPR) used by the cost calculator.',
            ),
        ),
    ]
