from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_destinationcountry_estimated_cost'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contactmessage',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='destinationcountry',
            options={'ordering': ['name_en']},
        ),
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ['-joined_date']},
        ),
        migrations.AlterModelOptions(
            name='resourcepublication',
            options={'ordering': ['-id']},
        ),
    ]
