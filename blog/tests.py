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
