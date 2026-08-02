from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Article
from members.models import Person


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8
    i18n = True

    def items(self):
        return [
            "index",
            "about",
            "counseling:request",
            "guidance",
            "safety",
            "resources",
            "blog:list",
            "members:member_list",
            "membership_information",
            "programs",
            "faq",
            "privacy",
            "disclaimer",
            "contact",
        ]

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.7
    i18n = True

    def items(self):
        return Article.objects.published()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class MemberSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.4
    i18n = True

    def items(self):
        return Person.objects.filter(
            is_public=True,
            merged_into__isnull=True,
            memberships__is_public=True,
            memberships__status__in=(
                "active", "inactive", "pending", "expired", "suspended"
            ),
        ).distinct()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("members:member_detail", kwargs={"public_id": obj.public_id})
