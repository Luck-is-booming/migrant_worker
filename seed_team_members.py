from core.models import TeamMember

TEAM_MEMBERS = [
    {
        "sort_order": 1,
        "name": "नविन सुन्दर सेर्मा",
        "address": "इलाम नगरपालिका - ७",
        "designation": "अध्यक्ष",
        "phone": "9817913334",
    },
    {
        "sort_order": 2,
        "name": "टिकाराम वराइली",
        "address": "देउमाइ नगरपालिका - १",
        "designation": "उपाध्यक्ष",
        "phone": "9763712498",
    },
    {
        "sort_order": 3,
        "name": "हेमन्त आचार्य",
        "address": "इलाम नगरपालिका - ५",
        "designation": "सचिव",
        "phone": "9848711834",
    },
    {
        "sort_order": 4,
        "name": "रन्जना लिम्बु",
        "address": "सुर्योदय नगरपालिका - १",
        "designation": "सह-सचिव",
        "phone": "9863621780",
    },
    {
        "sort_order": 5,
        "name": "इन्द्र कुमार तामाङ्",
        "address": "सूर्योदय नगरपालिका- १०",
        "designation": "कोषाध्यक्ष",
        "phone": "9744336662",
    },
    {
        "sort_order": 6,
        "name": "टङ्क प्रसाद पराजुली",
        "address": "देउमाइ नगरपालिका- ४",
        "designation": "सदस्य",
        "phone": "",
    },
    {
        "sort_order": 7,
        "name": "संगीता बराइली",
        "address": "इलाम नगरपालिका - ६",
        "designation": "सदस्य",
        "phone": "",
    },
    {
        "sort_order": 8,
        "name": "गेशव खतीवडा",
        "address": "सन्दकपुर गाउपालिका- ३",
        "designation": "सदस्य",
        "phone": "",
    },
    {
        "sort_order": 9,
        "name": "ज्योती खड्का",
        "address": "इलाम नगरपालिका - ६",
        "designation": "सदस्य",
        "phone": "",
    },
    {
        "sort_order": 10,
        "name": "टिका खत्री चोहान",
        "address": "इलाम नगरपालिका - ९",
        "designation": "सदस्य",
        "phone": "",
    },
    {
        "sort_order": 11,
        "name": "दोर्ण राज योङहाङ",
        "address": "माङ्सेवुङ् गाउंपालिका - ३",
        "designation": "सदस्य",
        "phone": "",
    },
]

for member in TEAM_MEMBERS:
    TeamMember.objects.update_or_create(
        name=member["name"],
        defaults={
            "address": member["address"],
            "designation": member["designation"],
            "phone": member["phone"],
            "sort_order": member["sort_order"],
            "is_active": True,
        },
    )

print(f"Seeded/updated {len(TEAM_MEMBERS)} team members.")
