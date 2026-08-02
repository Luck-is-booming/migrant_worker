from django.db import migrations
from django.db.models import Q


LEGACY_REPLACEMENTS = (
    {
        "match_title_en": "Process counseling",
        "match_title_ne": "प्रक्रिया बुझ्ने परामर्श",
        "match_desc_en": "Help understanding stages, documents, cost questions, and practical official verification steps.",
        "match_desc_ne": "वैदेशिक रोजगारको चरण, कागजात, लागतसम्बन्धी प्रश्न र आधिकारिक जाँचका उपाय बुझ्न सहयोग।",
        "title_en": "Understand the process",
        "title_ne": "प्रक्रिया बुझ्न सहयोग",
        "desc_en": (
            "We explain documents, contracts, costs, labor approval, insurance, "
            "and preparation before departure."
        ),
        "desc_ne": (
            "हामी कागजात, करार, खर्च, श्रम स्वीकृति, बीमा र प्रस्थानपूर्व "
            "तयारीबारे बुझाउँछौं।"
        ),
        "process_en": "Send your question or problem through the private counseling form.",
        "process_ne": "आफ्नो प्रश्न वा समस्या गोप्य परामर्श फाराममार्फत पठाउनुहोस्।",
    },
    {
        "match_title_en": "Risk and fraud awareness",
        "match_title_ne": "जोखिम र ठगी सचेतना",
        "match_desc_en": "Help recognizing suspicious offers, unclear fees, inconsistent contracts, and pressure to pay.",
        "match_desc_ne": "शंकास्पद प्रस्ताव, अस्पष्ट शुल्क, फरक करार र दबाबपूर्ण भुक्तानीका संकेत चिन्न सहयोग।",
        "title_en": "Recognize fraud and risk",
        "title_ne": "ठगी र जोखिम चिन्न सहयोग",
        "desc_en": (
            "We help you identify suspicious offers, hidden fees, mismatched "
            "contracts, and pressure to pay."
        ),
        "desc_ne": (
            "हामी शंकास्पद प्रस्ताव, लुकाइएका शुल्क, नमिलेका करार र पैसा "
            "तिर्ने दबाबका संकेत चिन्न सहयोग गर्छौं।"
        ),
        "process_en": "Check written evidence and official sources before making a decision.",
        "process_ne": "निर्णय लिनुअघि लिखित प्रमाण र आधिकारिक स्रोत जाँच गर्नुहोस्।",
    },
    {
        "match_title_en": "Appropriate referral",
        "match_title_ne": "उपयुक्त निकायमा मार्गदर्शन",
        "match_desc_en": "Help finding relevant government, embassy, labor, welfare, legal, medical, or emergency channels.",
        "match_desc_ne": "आवश्यकताअनुसार सरकारी, दूतावास, श्रम, कल्याण, कानुनी वा आपतकालीन निकाय खोज्न सहयोग।",
        "title_en": "Find the right office or service",
        "title_ne": "सम्बन्धित निकाय खोज्न सहयोग",
        "desc_en": (
            "We guide you to the relevant government office, embassy, labor "
            "authority, welfare service, or qualified professional."
        ),
        "desc_ne": (
            "हामी तपाईंलाई आवश्यक सरकारी कार्यालय, दूतावास, श्रम निकाय, "
            "कल्याण सेवा वा योग्य विशेषज्ञसम्म पुग्न मार्गदर्शन गर्छौं।"
        ),
        "process_en": "For an emergency, contact the relevant emergency service immediately.",
        "process_ne": "आपतकालीन अवस्थामा सम्बन्धित आपतकालीन सेवामा तुरुन्त सम्पर्क गर्नुहोस्।",
    },
)


def refresh_legacy_service_copy(apps, schema_editor):
    """Replace only known stock copy, never custom administrator-written services."""

    ServiceCard = apps.get_model("core", "ServiceCard")
    database = schema_editor.connection.alias
    for replacement in LEGACY_REPLACEMENTS:
        matches = ServiceCard.objects.using(database).filter(
            Q(
                title_en=replacement["match_title_en"],
                desc_en=replacement["match_desc_en"],
            )
            | Q(
                title_ne=replacement["match_title_ne"],
                desc_ne=replacement["match_desc_ne"],
            )
        )
        for service in matches:
            service.title_en = replacement["title_en"]
            service.title_ne = replacement["title_ne"]
            service.desc_en = replacement["desc_en"]
            service.desc_ne = replacement["desc_ne"]
            service.process_en = replacement["process_en"]
            service.process_ne = replacement["process_ne"]
            service.save(
                update_fields=(
                    "title_en",
                    "title_ne",
                    "desc_en",
                    "desc_ne",
                    "process_en",
                    "process_ne",
                )
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0015_alter_contactmessage_consent_recorded_at_and_more")]

    operations = [
        migrations.RunPython(refresh_legacy_service_copy, migrations.RunPython.noop),
    ]
