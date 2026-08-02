from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import FrequentlyAskedQuestion, OfficialResource, ResourceCategory


RESOURCES = [
    {
        "title_en": "Department of Foreign Employment",
        "title_ne": "वैदेशिक रोजगार विभाग",
        "description_en": "Official foreign-employment services, notices, labor-approval information, and complaint channels.",
        "description_ne": "वैदेशिक रोजगारसम्बन्धी सरकारी सेवा, सूचना, श्रम स्वीकृति जानकारी र उजुरीसम्बन्धी आधिकारिक स्रोत।",
        "url": "https://dofe.gov.np/",
    },
    {
        "title_en": "Foreign Employment Board Secretariat",
        "title_ne": "वैदेशिक रोजगार बोर्ड सचिवालय",
        "description_en": "Official worker-welfare, support, compensation, and returnee-worker information.",
        "description_ne": "श्रमिक कल्याण, सहायता, क्षतिपूर्ति र फर्किएका श्रमिकसम्बन्धी आधिकारिक जानकारी।",
        "url": "https://feb.gov.np/",
    },
    {
        "title_en": "Foreign Employment Information Management System (FEIMS)",
        "title_ne": "वैदेशिक रोजगार सूचना व्यवस्थापन प्रणाली (FEIMS)",
        "description_en": "Official digital system used for foreign-employment services and labor-approval processes.",
        "description_ne": "वैदेशिक रोजगार सेवा र श्रम स्वीकृति प्रक्रियामा प्रयोग हुने आधिकारिक डिजिटल प्रणाली।",
        "url": "https://feims.dofe.gov.np/",
    },
    {
        "title_en": "Foreign Job and Recruitment Information",
        "title_ne": "वैदेशिक रोजगार र इजाजतप्राप्त संस्थासम्बन्धी जानकारी",
        "description_en": "Official tools for reviewing recruitment agencies, pre-permission details, and approved foreign-job information.",
        "description_ne": "इजाजतप्राप्त संस्था, पूर्व स्वीकृति विवरण र स्वीकृत वैदेशिक रोजगारीसम्बन्धी जानकारी जाँच्ने आधिकारिक साधन।",
        "url": "https://foreignjob.dofe.gov.np/",
    },
    {
        "title_en": "Ministry of Labour, Employment and Social Security",
        "title_ne": "श्रम, रोजगार तथा सामाजिक सुरक्षा मन्त्रालय",
        "description_en": "Official policies, notices, laws, and institutional information from the responsible ministry.",
        "description_ne": "सम्बन्धित मन्त्रालयका नीति, सूचना, कानुन र संस्थागत जानकारीको आधिकारिक स्रोत।",
        "url": "https://moless.gov.np/",
    },
]

FAQS = [
    (
        "Does MRN Ilam arrange jobs or visas?",
        "के MRN इलामले रोजगारी वा भिसाको व्यवस्था गर्छ?",
        "No. MRN Ilam provides information, awareness, counseling, and referrals. It is not a recruitment, manpower, visa, or travel agency.",
        "गर्दैन। MRN इलामले सूचना, सचेतना, परामर्श र आवश्यक निकायमा सहजीकरण प्रदान गर्छ। यो म्यानपावर, भर्ती, भिसा वा ट्राभल एजेन्सी होइन।",
    ),
    (
        "Do I need to become a member to request counseling?",
        "परामर्श लिन सदस्य बन्नुपर्छ?",
        "No. Counseling is separate from membership and does not require a membership payment.",
        "पर्दैन। परामर्श सदस्यताभन्दा अलग सेवा हो र सदस्यता शुल्क तिर्नु आवश्यक छैन।",
    ),
    (
        "When does a membership become active?",
        "सदस्यता कहिले सक्रिय हुन्छ?",
        "A membership becomes active only after authorized staff review the application and payment evidence and approve it.",
        "अधिकृत कर्मचारीले आवेदन र भुक्तानी प्रमाण जाँच गरी स्वीकृत गरेपछि मात्र सदस्यता सक्रिय हुन्छ।",
    ),
    (
        "Can one person hold more than one membership?",
        "एउटै व्यक्तिको एकभन्दा बढी सदस्यता हुन सक्छ?",
        "Yes. A person may hold separate valid memberships, each with its own category, unit, status, and permanent number.",
        "हुन सक्छ। एउटै व्यक्तिले फरक प्रकार वा एकाइका वैध सदस्यता राख्न सक्छ, र प्रत्येकको छुट्टै प्रकार, एकाइ, स्थिति र स्थायी नम्बर हुन्छ।",
    ),
]


class Command(BaseCommand):
    help = "Create reviewed bilingual starter resources and FAQs without overwriting admin content."

    def handle(self, *args, **options):
        category, _ = ResourceCategory.objects.get_or_create(
            slug="official-government-services",
            defaults={
                "name_en": "Official government services",
                "name_ne": "आधिकारिक सरकारी सेवा",
                "display_order": 10,
                "is_active": True,
            },
        )
        created_resources = 0
        for order, item in enumerate(RESOURCES, start=10):
            _, created = OfficialResource.objects.get_or_create(
                url=item["url"],
                defaults={
                    **item,
                    "category": category,
                    "is_official_source": True,
                    "language": "both",
                    "display_order": order,
                    "is_active": True,
                    "last_reviewed": timezone.localdate(),
                },
            )
            created_resources += int(created)

        created_faqs = 0
        for order, (question_en, question_ne, answer_en, answer_ne) in enumerate(FAQS, start=10):
            _, created = FrequentlyAskedQuestion.objects.get_or_create(
                question_en=question_en,
                defaults={
                    "question_ne": question_ne,
                    "answer_en": answer_en,
                    "answer_ne": answer_ne,
                    "display_order": order,
                    "is_active": True,
                },
            )
            created_faqs += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"Launch content ready: {created_resources} resources and {created_faqs} FAQs created. Existing records were not overwritten."
        ))
