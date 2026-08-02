from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language

from .models import Article


def article_list(request):
    selected_type = request.GET.get("type", "").strip()[:30]
    language = get_language() or "ne"
    articles = Article.objects.published().filter(language__in=["both", language])
    if selected_type:
        articles = articles.filter(article_type=selected_type)
    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/article_list.html", {"page_obj": page_obj, "selected_type": selected_type, "type_choices": Article.TYPE_CHOICES})


def article_detail(request, slug):
    language = get_language() or "ne"
    article = get_object_or_404(
        Article.objects.published().filter(language__in=["both", language]),
        slug=slug,
    )
    return render(request, "blog/article_detail.html", {"article": article})
