from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("blog", "0005_professional_publishing")]

    operations = [
        migrations.AddField(model_name="article", name="image_alt_ne", field=models.CharField(blank=True, max_length=255, verbose_name="Image description (Nepali)")),
        migrations.AddField(model_name="article", name="image_alt_en", field=models.CharField(blank=True, max_length=255, verbose_name="Image description (English)")),
        migrations.AddField(model_name="article", name="expires_at", field=models.DateTimeField(blank=True, db_index=True, help_text="Optional. After this time the item is automatically hidden from public pages.", null=True, verbose_name="Expiry date")),
    ]
