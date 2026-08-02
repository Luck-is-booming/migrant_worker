from django import template
from django.urls import NoReverseMatch, reverse
from django.utils import translation

register = template.Library()

SAFE_QUERY_PARAMETERS = {
    "q",
    "category",
    "status",
    "unit",
    "type",
    "page",
}


@register.simple_tag(takes_context=True)
def translated_url(context, language_code):
    """Return the equivalent URL in another language, preserving safe filters."""
    request = context.get("request")
    if not request or not getattr(request, "resolver_match", None):
        return f"/{language_code}/"
    match = request.resolver_match
    current = translation.get_language()
    try:
        translation.activate(language_code)
        try:
            path = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
        except NoReverseMatch:
            path = f"/{language_code}/"
    finally:
        translation.activate(current)

    params = request.GET.copy()
    for key in list(params):
        if key not in SAFE_QUERY_PARAMETERS:
            params.pop(key, None)
    query = params.urlencode()
    return f"{path}?{query}" if query else path
