from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("blog", "0006_accessible_media_and_expiry")]

    operations = [
        migrations.AddField(
            model_name="article",
            name="meta_title_ne",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="article",
            name="meta_title_en",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="article",
            name="meta_description_ne",
            field=models.CharField(blank=True, max_length=320),
        ),
        migrations.AddField(
            model_name="article",
            name="meta_description_en",
            field=models.CharField(blank=True, max_length=320),
        ),
    ]
