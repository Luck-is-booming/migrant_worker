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
            "disclaimer_en": organization.disclaimer_en if organization else "We provide information and counseling. We do not arrange jobs or visas and cannot guarantee any result.",
            "disclaimer_ne": organization.disclaimer_ne if organization else "हामी सूचना र परामर्श प्रदान गर्छौं। हामी रोजगारी वा भिसाको व्यवस्था गर्दैनौं र कुनै नतिजाको ग्यारेन्टी दिँदैनौं।",
        }
        cache.set("public-organization-info", info, 300)
    return {"site_info": info, "current_year": timezone.now().year}
