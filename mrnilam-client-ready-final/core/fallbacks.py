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
            "title": "प्रक्रिया बुझ्ने परामर्श",
            "desc": "वैदेशिक रोजगारको चरण, कागजात, लागतसम्बन्धी प्रश्न र आधिकारिक जाँचका उपाय बुझ्न सहयोग।",
            "process": "निजी परामर्श अनुरोधमार्फत आफ्नो प्रश्न वा चिन्ता पठाउनुहोस्।",
            "icon": "guidance",
        },
        {
            "title": "जोखिम र ठगी सचेतना",
            "desc": "शंकास्पद प्रस्ताव, अस्पष्ट शुल्क, फरक करार र दबाबपूर्ण भुक्तानीका संकेत चिन्न सहयोग।",
            "process": "अन्तिम निर्णयअघि लिखित प्रमाण र आधिकारिक स्रोत जाँच गर्नुहोस्।",
            "icon": "shield",
        },
        {
            "title": "उपयुक्त निकायमा मार्गदर्शन",
            "desc": "आवश्यकताअनुसार सरकारी, दूतावास, श्रम, कल्याण, कानुनी वा आपतकालीन निकाय खोज्न सहयोग।",
            "process": "यो सेवा आपतकालीन प्रतिक्रिया वा कानुनी प्रतिनिधित्व होइन।",
            "icon": "rights",
        },
    ],
    "en": [
        {
            "title": "Process counseling",
            "desc": "Help understanding stages, documents, cost questions, and practical official verification steps.",
            "process": "Send the question or concern through the private counseling request.",
            "icon": "guidance",
        },
        {
            "title": "Risk and fraud awareness",
            "desc": "Help recognizing suspicious offers, unclear fees, inconsistent contracts, and pressure to pay.",
            "process": "Verify written evidence and official sources before making a final decision.",
            "icon": "shield",
        },
        {
            "title": "Appropriate referral",
            "desc": "Help finding relevant government, embassy, labor, welfare, legal, medical, or emergency channels.",
            "process": "This service is not emergency response or legal representation.",
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
