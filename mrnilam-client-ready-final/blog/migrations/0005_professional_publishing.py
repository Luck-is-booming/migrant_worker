from django.db import migrations, models
import django.utils.timezone


def seed_existing(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    from django.utils.text import slugify

    for article in Article.objects.all().order_by("pk"):
        base = slugify(article.title_en) or f"article-{article.pk}"
        slug = base
        counter = 2
        while Article.objects.exclude(pk=article.pk).filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1
        article.slug = slug
        article.status = "published"
        article.article_type = "alert" if article.is_alert else "article"
        article.alert_severity = "urgent" if article.is_alert else ""
        article.save(update_fields=["slug", "status", "article_type", "alert_severity"])


class Migration(migrations.Migration):
    dependencies = [("blog", "0004_rename_blog_articl_is_aler_idx_blog_articl_is_aler_5de6f5_idx")]

    operations = [
        migrations.AddField(model_name="article", name="slug", field=models.SlugField(blank=True, db_index=False, max_length=280, null=True)),
        migrations.AddField(model_name="article", name="summary_ne", field=models.TextField(blank=True, max_length=600, verbose_name="Summary (Nepali)")),
        migrations.AddField(model_name="article", name="summary_en", field=models.TextField(blank=True, max_length=600, verbose_name="Summary (English)")),
        migrations.AddField(model_name="article", name="article_type", field=models.CharField(choices=[("article", "Article"), ("notice", "Notice"), ("alert", "Safety alert"), ("event", "Event"), ("counseling_update", "Counseling update")], db_index=True, default="article", max_length=30)),
        migrations.AddField(model_name="article", name="status", field=models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], db_index=True, default="draft", max_length=20)),
        migrations.AddField(model_name="article", name="updated_at", field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name="article", name="author_name", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="article", name="language", field=models.CharField(choices=[("both", "Both"), ("ne", "Nepali"), ("en", "English")], default="both", max_length=10)),
        migrations.AddField(model_name="article", name="is_featured", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="article", name="alert_severity", field=models.CharField(blank=True, choices=[("", "Not an alert"), ("info", "Information"), ("important", "Important"), ("urgent", "Urgent")], max_length=20)),
        migrations.AddField(model_name="article", name="meta_title", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="article", name="meta_description", field=models.CharField(blank=True, max_length=320)),
        migrations.RunPython(seed_existing, migrations.RunPython.noop),
        migrations.AlterField(model_name="article", name="slug", field=models.SlugField(blank=True, max_length=280, unique=True)),
        migrations.AlterField(model_name="article", name="published_date", field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="Published Date")),
        migrations.AlterModelOptions(name="article", options={"ordering": ["-is_featured", "-published_date"], "verbose_name": "Article", "verbose_name_plural": "Articles"}),
        migrations.RemoveIndex(model_name="article", name="blog_articl_is_aler_5de6f5_idx"),
        migrations.AddIndex(model_name="article", index=models.Index(fields=["status", "-published_date"], name="blog_articl_status_5e4672_idx")),
        migrations.AddIndex(model_name="article", index=models.Index(fields=["article_type", "status"], name="blog_articl_article_bc14eb_idx")),
    ]
