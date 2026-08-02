"""Conservative public fallback content.

Fallbacks explain the service without inventing staff, contacts, achievements,
partnerships, statistics, dates, or authority claims. Authorized staff should
replace them with reviewed database content.
"""

FALLBACK_INFO = {
    "ne": {
        "name": "आप्रवासी कामदार हकहित संरक्षण केन्द्र, इलाम",
        "slogan": "सुरक्षित वैदेशिक रोजगार, समृद्ध परिवार र समृद्ध राष्ट्रको आधार।",
        "objective": "वैदेशिक रोजगारीलाई सुरक्षित, भरपर्दो, मर्यादित र उपलब्धिमूलक बनाउने।",
        "commitment": (
            "वैदेशिक रोजगारीबाट फर्किएका श्रमिकको सीप, पूँजी, प्रविधि र अनुभवलाई "
            "राष्ट्र निर्माणमा उच्चतम सार्थक उपयोग गर्ने।"
        ),
        "chairperson": "",
        "message": "",
    },
    "en": {
        "name": "Migrant Workers’ Rights Protection Centre, Ilam",
        "slogan": "Safe foreign employment is the foundation of prosperous families and a prosperous nation.",
        "objective": "To make foreign employment safe, reliable, dignified, and productive.",
        "commitment": (
            "To maximize the meaningful use of returnee migrant workers’ skills, capital, "
            "technology, and experience in nation-building."
        ),
        "chairperson": "",
        "message": "",
    },
}

FALLBACK_SERVICES = {
    "ne": [
        {
            "title": "प्रक्रिया बुझ्न सहयोग",
            "desc": "हामी कागजात, करार, खर्च, श्रम स्वीकृति, बीमा र प्रस्थानपूर्व तयारीबारे बुझाउँछौं।",
            "process": "आफ्नो प्रश्न वा समस्या गोप्य परामर्श फाराममार्फत पठाउनुहोस्।",
            "icon": "guidance",
        },
        {
            "title": "ठगी र जोखिम चिन्न सहयोग",
            "desc": "हामी शंकास्पद प्रस्ताव, लुकाइएका शुल्क, नमिलेका करार र पैसा तिर्ने दबाबका संकेत चिन्न सहयोग गर्छौं।",
            "process": "निर्णय लिनुअघि लिखित प्रमाण र आधिकारिक स्रोत जाँच गर्नुहोस्।",
            "icon": "shield",
        },
        {
            "title": "सम्बन्धित निकाय खोज्न सहयोग",
            "desc": "हामी तपाईंलाई आवश्यक सरकारी कार्यालय, दूतावास, श्रम निकाय, कल्याण सेवा वा योग्य विशेषज्ञसम्म पुग्न मार्गदर्शन गर्छौं।",
            "process": "आपतकालीन अवस्थामा सम्बन्धित आपतकालीन सेवामा तुरुन्त सम्पर्क गर्नुहोस्।",
            "icon": "rights",
        },
    ],
    "en": [
        {
            "title": "Understand the process",
            "desc": "We explain documents, contracts, costs, labor approval, insurance, and preparation before departure.",
            "process": "Send your question or problem through the private counseling form.",
            "icon": "guidance",
        },
        {
            "title": "Recognize fraud and risk",
            "desc": "We help you identify suspicious offers, hidden fees, mismatched contracts, and pressure to pay.",
            "process": "Check written evidence and official sources before making a decision.",
            "icon": "shield",
        },
        {
            "title": "Find the right office or service",
            "desc": "We guide you to the relevant government office, embassy, labor authority, welfare service, or qualified professional.",
            "process": "For an emergency, contact the relevant emergency service immediately.",
            "icon": "rights",
        },
    ],
}

# These remain empty until authorized staff add verified records in Django admin.
FALLBACK_COUNTRIES = {"ne": [], "en": []}
FALLBACK_RESOURCES = {"ne": [], "en": []}
FALLBACK_TEAM = {"ne": [], "en": []}
FALLBACK_ARTICLES = {"ne": [], "en": []}


def _lang_key(lang):
    return "ne" if lang == "ne" else "en"


def get_fallback_info(lang):
    return FALLBACK_INFO[_lang_key(lang)].copy()


def get_fallback_services(lang):
    return list(FALLBACK_SERVICES[_lang_key(lang)])


def get_fallback_countries(lang):
    return list(FALLBACK_COUNTRIES[_lang_key(lang)])


def get_fallback_resources(lang):
    return list(FALLBACK_RESOURCES[_lang_key(lang)])


def get_fallback_team(lang):
    return list(FALLBACK_TEAM[_lang_key(lang)])


def get_fallback_articles(lang):
    return list(FALLBACK_ARTICLES[_lang_key(lang)])
