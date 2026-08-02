from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone, translation

from .models import Article


class PublishingTests(TestCase):
    def make_article(self, status):
        return Article.objects.create(
            title_ne=f"शीर्षक {status}", title_en=f"Title {status}",
            content_ne="सामग्री", content_en="Content", status=status,
            published_date=timezone.now(),
        )

    def test_only_published_articles_are_public(self):
        published = self.make_article("published")
        draft = self.make_article("draft")
        with translation.override("en"):
            response = self.client.get(reverse("blog:list"))
            self.assertContains(response, published.title_en)
            self.assertNotContains(response, draft.title_en)
            self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)

    def test_expired_published_article_is_hidden(self):
        expired = Article.objects.create(
            title_ne="म्याद सकिएको सूचना",
            title_en="Expired notice",
            content_ne="सामग्री",
            content_en="Content",
            status="published",
            published_date=timezone.now() - timedelta(days=2),
            expires_at=timezone.now() - timedelta(hours=1),
        )
        with translation.override("en"):
            response = self.client.get(reverse("blog:list"))
            detail = self.client.get(expired.get_absolute_url())
        self.assertNotContains(response, expired.title_en)
        self.assertEqual(detail.status_code, 404)
