from django.utils import timezone
from django.utils.translation import get_language

from blog.models import Article
from members.models import Person

from .fallbacks import get_fallback_info, get_fallback_services, get_fallback_team
from .models import (
    EmergencyResource,
    FrequentlyAskedQuestion,
    OfficialResource,
    OrganizationInfo,
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
    "official_phone",
    "official_email",
    "office_address",
    "service_hours",
    "disclaimer",
    "registration_number",
    "registration_authority",
    "established_date",
    "service_area",
)


def _info_context(db_info, lang):
    if db_info:
        return {field: getattr(db_info, field, None) for field in INFO_FIELDS}
    fallback = get_fallback_info(lang)
    fallback.update(
        {
            "chairperson_photo": None,
            "official_phone": "",
            "official_email": "",
            "office_address": "",
            "service_hours": "",
            "registration_number": "",
            "registration_authority": "",
            "established_date": None,
            "service_area": "",
            "disclaimer": (
                "हामी वैदेशिक रोजगारसम्बन्धी सूचना, सचेतना र परामर्श प्रदान गर्छौं। "
                "हामी भिसा जारी गर्दैनौं वा रोजगारीको ग्यारेन्टी गर्दैनौं।"
                if lang == "ne"
                else "We provide foreign-employment information, awareness, and counseling. "
                "We do not issue visas or guarantee employment."
            ),
        }
    )
    return fallback


def build_site_context():
    lang = get_language() or "ne"
    info = _info_context(OrganizationInfo.objects.first(), lang)
    services = list(ServiceCard.objects.filter(is_active=True)) or get_fallback_services(lang)
    team = list(TeamMember.objects.filter(is_active=True)) or get_fallback_team(lang)
    latest_articles = list(
        Article.objects.published().filter(language__in=["both", lang])[:3]
    )
    return {
        "info": info,
        "services": services,
        "team_members": team,
        "latest_articles": latest_articles,
        "featured_resources": OfficialResource.objects.filter(
            is_active=True, language__in=["both", lang]
        ).select_related("category")[:6],
        "emergency_resources": EmergencyResource.objects.filter(is_active=True)[:4],
        "faqs": FrequentlyAskedQuestion.objects.filter(is_active=True)[:8],
        "member_count": Person.objects.filter(
            is_public=True,
            merged_into__isnull=True,
            memberships__is_public=True,
            memberships__status__in=(
                "active", "inactive", "pending", "expired", "suspended"
            ),
        ).distinct().count(),
        "current_year": timezone.now().year,
    }


def build_homepage_context():
    return build_site_context()
