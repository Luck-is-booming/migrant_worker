from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 1.0

    # Generate entries for every language in settings.LANGUAGES
    i18n = True

    def items(self):
        return [
            "index",
            "members:member_list",
        ]

    def location(self, item):
        return reverse(item)