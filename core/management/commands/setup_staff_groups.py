from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


ROLE_RULES = {
    "Membership Manager": {
        "members": [
            "view_person", "add_person", "change_person",
            "view_membershiprecord", "add_membershiprecord", "change_membershiprecord",
            "view_membershipcategory", "view_organizationunit",
            "view_importbatch", "view_importrowrecord", "view_potentialduplicate",
            "change_potentialduplicate",
        ],
        "core": ["view_membership", "change_membership"],
    },
    "Counseling Staff": {
        "counseling": [
            "view_counselingrequest", "change_counselingrequest", "assign_counselingrequest",
            "view_counselingcategory", "view_counselingnote", "add_counselingnote",
            "change_counselingnote", "view_contactattempt", "add_contactattempt",
            "change_contactattempt",
        ],
    },
    "Content Editor": {
        "blog": ["add_article", "change_article", "view_article"],
        "core": [
            "view_organizationinfo", "change_organizationinfo",
            "add_servicecard", "change_servicecard", "view_servicecard",
            "add_officialresource", "change_officialresource", "view_officialresource",
            "add_resourcecategory", "change_resourcecategory", "view_resourcecategory",
            "add_frequentlyaskedquestion", "change_frequentlyaskedquestion", "view_frequentlyaskedquestion",
            "add_emergencyresource", "change_emergencyresource", "view_emergencyresource",
            "add_teammember", "change_teammember", "view_teammember",
        ],
    },
    "Payment Reviewer": {
        "payments": [
            "view_manualpayment", "change_manualpayment",
            "view_paymentreviewevent",
        ],
        "core": ["view_membership"],
    },
}


class Command(BaseCommand):
    help = "Create least-privilege staff groups and assign model permissions."

    def handle(self, *args, **options):
        for group_name, app_rules in ROLE_RULES.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            selected = []
            missing = []
            for app_label, codenames in app_rules.items():
                for codename in codenames:
                    permission = Permission.objects.filter(
                        content_type__app_label=app_label,
                        codename=codename,
                    ).first()
                    if permission:
                        selected.append(permission)
                    else:
                        missing.append(f"{app_label}.{codename}")
            group.permissions.set(selected)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Configured {group_name} with {len(selected)} permissions."
                )
            )
            if missing:
                self.stdout.write(self.style.WARNING("Missing: " + ", ".join(missing)))

        administrator, _ = Group.objects.get_or_create(name="Administrator")
        administrator.permissions.set(Permission.objects.all())
        self.stdout.write(self.style.SUCCESS("Configured Administrator with all model permissions."))
