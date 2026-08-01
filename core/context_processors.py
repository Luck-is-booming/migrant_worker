from django.core.cache import cache
from django.utils import timezone

from .models import OrganizationInfo


def public_site_settings(request):
    info = cache.get("public-organization-info")
    if info is None:
        organization = OrganizationInfo.objects.first()
        info = {
            "name_en": organization.name_en if organization else "MRN Ilam",
            "name_ne": organization.name_ne if organization else "आप्रवासी कामदार हकहित संरक्षण केन्द्र, इलाम",
            "phone": organization.official_phone if organization else "",
            "email": organization.official_email if organization else "",
            "address_en": organization.office_address_en if organization else "",
            "address_ne": organization.office_address_ne if organization else "",
            "disclaimer_en": organization.disclaimer_en if organization else "We provide information, awareness, and counseling. We do not issue visas or guarantee jobs.",
            "disclaimer_ne": organization.disclaimer_ne if organization else "हामी सूचना, सचेतना र परामर्श प्रदान गर्छौं। हामी भिसा जारी गर्दैनौं वा रोजगारीको ग्यारेन्टी गर्दैनौं।",
        }
        cache.set("public-organization-info", info, 300)
    return {"site_info": info, "current_year": timezone.now().year}
