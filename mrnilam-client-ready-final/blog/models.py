from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

import nepali_datetime

from core.i18n_utils import localized


DEFAULT_ARTICLE_IMAGE = ""


class ArticleQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(
            status="published",
            published_date__lte=now,
        ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))


class Article(models.Model):
    TYPE_CHOICES = [
        ("article", _("Article")),
        ("notice", _("Notice")),
        ("alert", _("Safety alert")),
        ("event", _("Event")),
        ("counseling_update", _("Counseling update")),
    ]
    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("published", _("Published")),
        ("archived", _("Archived")),
    ]
    SEVERITY_CHOICES = [
        ("", _("Not an alert")),
        ("info", _("Information")),
        ("important", _("Important")),
        ("urgent", _("Urgent")),
    ]

    title_ne = models.CharField(_("Title (Nepali)"), max_length=255)
    title_en = models.CharField(_("Title (English)"), max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    summary_ne = models.TextField(_("Summary (Nepali)"), blank=True, max_length=600)
    summary_en = models.TextField(_("Summary (English)"), blank=True, max_length=600)
    content_ne = models.TextField(_("Content (Nepali)"))
    content_en = models.TextField(_("Content (English)"))
    article_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="article", db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    featured_image_url = models.URLField(_("Featured Image URL"), max_length=500, blank=True, null=True)
    featured_image_file = models.ImageField(_("Upload Photo from Device"), upload_to="blog_photos/", blank=True, null=True)
    image_alt_ne = models.CharField(_("Image description (Nepali)"), max_length=255, blank=True)
    image_alt_en = models.CharField(_("Image description (English)"), max_length=255, blank=True)
    published_date = models.DateTimeField(_("Published Date"), default=timezone.now, db_index=True)
    expires_at = models.DateTimeField(
        _("Expiry date"), null=True, blank=True, db_index=True,
        help_text=_("Optional. After this time the item is automatically hidden from public pages."),
    )
    updated_at = models.DateTimeField(auto_now=True)
    author_name = models.CharField(max_length=180, blank=True)
    language = models.CharField(max_length=10, choices=[("both", _("Both")), ("ne", _("Nepali")), ("en", _("English"))], default="both")
    is_featured = models.BooleanField(default=False)
    is_alert = models.BooleanField(_("Is Critical Emergency Alert?"), default=False)
    alert_severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, blank=True)
    # Legacy single-language metadata is retained for migration/audit only.
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    meta_title_ne = models.CharField(max_length=255, blank=True)
    meta_title_en = models.CharField(max_length=255, blank=True)
    meta_description_ne = models.CharField(max_length=320, blank=True)
    meta_description_en = models.CharField(max_length=320, blank=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-is_featured", "-published_date"]
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        indexes = [
            models.Index(fields=["status", "-published_date"]),
            models.Index(fields=["article_type", "status"]),
        ]

    @property
    def title(self):
        return localized(self.title_ne, self.title_en)

    @property
    def summary(self):
        value = localized(self.summary_ne, self.summary_en)
        if value:
            return value
        content = self.content
        return content[:240] + ("…" if len(content) > 240 else "")

    @property
    def content(self):
        return localized(self.content_ne, self.content_en)

    @property
    def image_alt(self):
        return localized(self.image_alt_ne, self.image_alt_en) or self.title


    @property
    def seo_title(self):
        return localized(self.meta_title_ne, self.meta_title_en) or self.title

    @property
    def seo_description(self):
        return localized(self.meta_description_ne, self.meta_description_en) or self.summary

    @property
    def image_url(self):
        if self.featured_image_file:
            try:
                return self.featured_image_file.url
            except (ValueError, OSError):
                pass
        return (self.featured_image_url or "").strip()

    @property
    def formatted_date(self):
        from django.utils.translation import get_language

        if get_language() == "ne":
            nepali_date = nepali_datetime.date.from_datetime_date(self.published_date.date())
            return nepali_date.strftime("%K %N %D गते")
        return self.published_date.strftime("%B %d, %Y")

    def save(self, *args, **kwargs):
        if self.is_alert and self.article_type == "article":
            self.article_type = "alert"
        if self.article_type == "alert":
            self.is_alert = True
        if not self.slug:
            base = slugify(self.title_en) or f"article-{timezone.now():%Y%m%d}"
            candidate = base
            count = 2
            while Article.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
                candidate = f"{base}-{count}"
                count += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title_en
