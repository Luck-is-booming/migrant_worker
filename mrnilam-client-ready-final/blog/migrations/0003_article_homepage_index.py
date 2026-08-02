from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_article_options_article_featured_image_file'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={
                'ordering': ['-published_date'],
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
            },
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['-is_alert', '-published_date'], name='blog_articl_is_aler_idx'),
        ),
    ]
