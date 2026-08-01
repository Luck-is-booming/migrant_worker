from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Article


def article_list(request):
    selected_type = request.GET.get("type", "").strip()[:30]
    articles = Article.objects.published()
    if selected_type:
        articles = articles.filter(article_type=selected_type)
    paginator = Paginator(articles, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/article_list.html", {"page_obj": page_obj, "selected_type": selected_type, "type_choices": Article.TYPE_CHOICES})


def article_detail(request, slug):
    article = get_object_or_404(Article.objects.published(), slug=slug)
    return render(request, "blog/article_detail.html", {"article": article})
