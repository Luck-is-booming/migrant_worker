BOOK_ICON = (
    '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
    'd="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 '
    '7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 '
    '18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>'
)
LEGAL_ICON = (
    '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
    'd="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"></path></svg>'
)

FALLBACK_INFO = {
    'ne': {
        'name': 'आप्रवासी कामदार हकहित संरक्षण केन्द्र, इलाम',
        'slogan': 'सुरक्षित वैदेशिक रोजगार, समृद्ध परिवार र समृद्ध राष्ट्रको आधार।',
        'objective': 'वैदेशिक रोजगारीलाई सुरक्षित, भरपर्दो, मर्यादित र उपलब्धिमूलक बनाउने।',
        'commitment': 'वैदेशिक रोजगारीबाट फर्किएका श्रमिकको सीप, पूँजी, प्रविधि र अनुभवको राष्ट्र निर्माणमा उच्चतम सार्थक उपयोग गर्ने।',
        'chairperson': 'राम बहादुर गुरुङ',
        'message': 'वैदेशिक रोजगारीमा जाने प्रत्येक नेपाली नागरिकको अधिकार र सुरक्षा सुनिश्चित गर्नु हाम्रो परम कर्तव्य हो। इलाम जिल्ला र आसपासका क्षेत्रमा सचेतना फैलाउन हामी निरन्तर प्रतिबद्ध छौं।',
    },
    'en': {
        'name': 'Migrant Workers Rights and Welfare Protection Center, Ilam',
        'slogan': 'Safe Foreign Employment: The Foundation of a Prosperous Family and a Prosperous Nation.',
        'objective': 'To make foreign employment safe, reliable, dignified, and productive.',
        'commitment': 'To achieve the highest meaningful utilization of the skills, capital, technology, and experience of returnee migrant workers in nation-building.',
        'chairperson': 'Ram Bahadur Gurung',
        'message': 'Ensuring the safety, dignity, and legal rights of every migrant worker is our utmost duty. We continuously strive to build a transparent ecosystem from the grass-roots level upward.',
    },
}

FALLBACK_SERVICES = {
    'ne': [
        {
            'title': 'पूर्व-प्रस्थान परामर्श',
            'desc': 'श्रम सम्झौता, भिसा, बीमा र गन्तव्य देशको कानुनबारे विस्तृत जानकारी र अभिमुखीकरण परामर्श।',
            'process': 'केन्द्रको कार्यालयमा सक्कल राहदानी र श्रम इजाजत पत्र सहित सम्पर्क राख्ने।',
            'icon': BOOK_ICON,
        },
        {
            'title': 'कानुनी सहायता र उद्धार',
            'desc': 'अलपत्र परेका, ठगीमा परेका वा बन्धक बनाइएका श्रमिकहरूको कानुनी उपचार र द्रुत सरकारी उद्धार समन्वय।',
            'process': 'केन्द्रको आकस्मिक हेल्पलाईन नम्बर वा प्रमाण सहित अनलाइन फारम भर्ने।',
            'icon': LEGAL_ICON,
        },
    ],
    'en': [
        {
            'title': 'Pre-Departure Counselling',
            'desc': 'Comprehensive verification checks regarding employment contracts, medical benefits, insurance limits, and legal documentation.',
            'process': 'Visit our main physical helpdesk in Ilam with your valid passport draft copy.',
            'icon': BOOK_ICON,
        },
        {
            'title': 'Legal Aid & Emergency Rescue',
            'desc': 'Active cross-border coordination with local embassies, safe houses, and ministries to track down wage theft and coordinate rescue operations.',
            'process': 'Submit official contractual deployment complaints directly via our secure portals.',
            'icon': LEGAL_ICON,
        },
    ],
}

FALLBACK_COUNTRIES = {
    'ne': [
        {'name': 'मलेसिया', 'cost': 35000, 'flag': '🇲🇾'},
        {'name': 'कतार', 'cost': 25000, 'flag': '🇶🇦'},
    ],
    'en': [
        {'name': 'Malaysia', 'cost': 35000, 'flag': '🇲🇾'},
        {'name': 'Qatar', 'cost': 25000, 'flag': '🇶🇦'},
    ],
}

FALLBACK_RESOURCES = {
    'ne': [
        {'title': 'सुरक्षित वैदेशिक रोजगार हातेपुस्तिका २०२६', 'category': 'निर्देशिका र पुस्तिकाहरू', 'file_url': '#', 'size': '2.4 MB'},
        {'title': 'म्यानपावर एजेन्सी ठगी नियन्त्रण निर्देशिका', 'category': 'कानुनी दस्तावेज', 'file_url': '#', 'size': '1.1 MB'},
    ],
    'en': [
        {'title': 'Safe Foreign Employment Handbook 2026', 'category': 'Guides & Manuals', 'file_url': '#', 'size': '2.4 MB'},
        {'title': 'Manpower Agency Fraud Prevention Guide', 'category': 'Legal Resources', 'file_url': '#', 'size': '1.1 MB'},
    ],
}

FALLBACK_TEAM = {
    'ne': [
        {'name': 'सीता राजबंशी', 'designation': 'वरिष्ठ कानुनी अधिकारी', 'email': 'sita.legal@mrcilam.org', 'phone': '+९७७-२७-५२०१११', 'image': None},
        {'name': 'रमेश श्रेष्ठ', 'designation': 'मनोसामाजिक परामर्शदाता', 'email': 'ramesh.counselor@mrcilam.org', 'phone': '+९७७-२७-५२०२२२', 'image': None},
    ],
    'en': [
        {'name': 'Sita Rajbanshi', 'designation': 'Senior Legal Protection Officer', 'email': 'sita.legal@mrcilam.org', 'phone': '+977-27-520111', 'image': None},
        {'name': 'Ramesh Shrestha', 'designation': 'Lead Psychosocial Counselor', 'email': 'ramesh.counselor@mrcilam.org', 'phone': '+977-27-520222', 'image': None},
    ],
}

FALLBACK_ARTICLES = {
    'ne': [
        {
            'title': 'मलेसिया जाने कामदारहरूको लागि नयाँ स्वास्थ्य मापदण्ड',
            'content': 'मलेसिया सरकारले आगामी महिनादेखि लागू हुने गरी स्वास्थ्य परीक्षण मापदण्डमा परिमार्जन गरेको छ।',
            'image_url': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&auto=format&fit=crop',
            'formatted_date': '२०८३ जेठ २७ गते',
            'is_alert': True,
        }
    ],
    'en': [
        {
            'title': 'New Medical Examination Standards for Malaysia Bound Workers',
            'content': 'The government of Malaysia has announced updated diagnostic compliance criteria effective next month.',
            'image_url': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&auto=format&fit=crop',
            'formatted_date': 'June 10, 2026',
            'is_alert': True,
        }
    ],
}


def _lang_key(lang):
    return 'ne' if lang == 'ne' else 'en'


def get_fallback_info(lang):
    return FALLBACK_INFO[_lang_key(lang)]


def get_fallback_services(lang):
    return FALLBACK_SERVICES[_lang_key(lang)]


def get_fallback_countries(lang):
    return FALLBACK_COUNTRIES[_lang_key(lang)]


def get_fallback_resources(lang):
    return FALLBACK_RESOURCES[_lang_key(lang)]


def get_fallback_team(lang):
    return FALLBACK_TEAM[_lang_key(lang)]


def get_fallback_articles(lang):
    return FALLBACK_ARTICLES[_lang_key(lang)]
