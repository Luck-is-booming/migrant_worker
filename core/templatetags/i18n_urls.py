from django import template
from django.urls import NoReverseMatch, reverse
from django.utils import translation

register = template.Library()


@register.simple_tag(takes_context=True)
def translated_url(context, language_code):
    request = context.get("request")
    if not request or not getattr(request, "resolver_match", None):
        return "/"
    match = request.resolver_match
    current = translation.get_language()
    try:
        translation.activate(language_code)
        try:
            return reverse(match.view_name, args=match.args, kwargs=match.kwargs)
        except NoReverseMatch:
            return request.path
    finally:
        translation.activate(current)
