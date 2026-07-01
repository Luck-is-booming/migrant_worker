from django.utils import timezone
from django.utils.translation import get_language

from blog.models import Article

from .fallbacks import (
    get_fallback_articles,
    get_fallback_countries,
    get_fallback_info,
    get_fallback_resources,
    get_fallback_services,
    get_fallback_team,
)
from .models import (
    DestinationCountry,
    OrganizationInfo,
    ResourcePublication,
    ServiceCard,
    TeamMember,
)


INFO_FIELDS = (
    "name",
    "slogan",
    "objective",
    "commitment",
    "chairperson",
    "message",
    "chairperson_photo",
)

TEAM_MEMBER_FIELDS = (
    "name",
    "designation",
    "address",
    "email",
    "phone",
    "image",
    "sort_order",
)


def _info_context(db_info, lang):
    if db_info:
        return {field: getattr(db_info, field, None) for field in INFO_FIELDS}

    fallback_info = get_fallback_info(lang)
    fallback_info["chairperson_photo"] = None
    return fallback_info


def build_homepage_context():
    lang = get_language()

    info = _info_context(OrganizationInfo.objects.first(), lang)

    services = list(ServiceCard.objects.all())
    if not services:
        services = get_fallback_services(lang)

    countries = list(DestinationCountry.objects.all())
    if not countries:
        countries = get_fallback_countries(lang)

    resources = list(ResourcePublication.objects.all())
    if not resources:
        resources = get_fallback_resources(lang)

    team_members = list(
        TeamMember.objects.filter(is_active=True).only(*TEAM_MEMBER_FIELDS)
    )
    if not team_members:
        team_members = get_fallback_team(lang)

    latest_articles = list(
        Article.objects.order_by("-is_alert", "-published_date")[:3]
    )
    if not latest_articles:
        latest_articles = get_fallback_articles(lang)

    return {
        "info": info,
        "services": services,
        "countries": countries,
        "resources": resources,
        "team_members": team_members,
        "latest_articles": latest_articles,
        "current_year": timezone.now().year,
    }