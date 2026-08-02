from django.core.management.base import BaseCommand

from members.models import Member
from members.name_utils import romanize_nepali_name


class Command(BaseCommand):
    help = "Fill English names for existing members using Nepali name romanization"

    def handle(self, *args, **options):
        updated_count = 0

        members = Member.objects.all()

        for member in members:
            new_english_name = romanize_nepali_name(member.name_ne)

            if new_english_name and member.name_en != new_english_name:
                member.name_en = new_english_name
                member.save(update_fields=["name_en"])
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"English names filled. Updated: {updated_count}"
            )
        )