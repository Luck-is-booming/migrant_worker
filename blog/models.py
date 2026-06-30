from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import nepali_datetime

from core.i18n_utils import localized

DEFAULT_ARTICLE_IMAGE = "https://images.unsplash.com/photo-1450133064473-71024230f91b?q=80&w=600"


class Article(models.Model):
    title_ne = models.CharField(_("Title (Nepali)"), max_length=255)
    title_en = models.CharField(_("Title (English)"), max_length=255)
    content_ne = models.TextField(_("Content (Nepali)"))
    content_en = models.TextField(_("Content (English)"))
    featured_image_url = models.URLField(_("Featured Image URL"), max_length=500, blank=True, null=True)
    featured_image_file = models.ImageField(_("Upload Photo from Device"), upload_to='blog_photos/', blank=True, null=True)
    published_date = models.DateTimeField(_("Published Date"), default=timezone.now)
    is_alert = models.BooleanField(_("Is Critical Emergency Alert?"), default=False)

    class Meta:
        ordering = ['-published_date']
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        indexes = [
            models.Index(fields=['-is_alert', '-published_date']),
        ]

    @property
    def title(self):
        return localized(self.title_ne, self.title_en)

    @property
    def content(self):
        return localized(self.content_ne, self.content_en)

    @property
    def image_url(self):
        if self.featured_image_file:
            try:
                url_str = self.featured_image_file.url
                if url_str and "None" not in str(url_str) and url_str.strip():
                    return url_str
            except Exception:
                pass

        if self.featured_image_url and self.featured_image_url.strip():
            return self.featured_image_url.strip()

        return DEFAULT_ARTICLE_IMAGE

    @property
    def formatted_date(self):
        from django.utils.translation import get_language

        if get_language() == 'ne':
            nepali_date = nepali_datetime.date.from_datetime_date(self.published_date.date())
            return nepali_date.strftime('%K %N %D गते')
        return self.published_date.strftime('%B %d, %Y')

    def __str__(self):
        return self.title_en
