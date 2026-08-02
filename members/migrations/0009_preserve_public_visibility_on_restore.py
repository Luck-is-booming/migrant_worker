from django.db import migrations, models


KNOWN_UNIT_NAMES_NE = {
    "Ilam District": "इलाम जिल्ला",
    "Ilam Municipality": "इलाम नगरपालिका",
    "Deumai Municipality": "देउमाई नगरपालिका",
    "Suryodaya Municipality": "सूर्योदय नगरपालिका",
    "Phakphokthum Rural Municipality": "फाकफोकथुम गाउँपालिका",
    "Sandakpur Rural Municipality": "सन्दकपुर गाउँपालिका",
}


def fill_known_nepali_unit_names(apps, schema_editor):
    OrganizationUnit = apps.get_model("members", "OrganizationUnit")
    for name_en, name_ne in KNOWN_UNIT_NAMES_NE.items():
        OrganizationUnit.objects.filter(name_en=name_en, name_ne="").update(name_ne=name_ne)


class Migration(migrations.Migration):
    dependencies = [("members", "0008_reliable_membership_numbering")]

    operations = [
        migrations.AddField(
            model_name="membershiprecord",
            name="was_public_before_archive",
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.RunPython(fill_known_nepali_unit_names, migrations.RunPython.noop),
    ]
