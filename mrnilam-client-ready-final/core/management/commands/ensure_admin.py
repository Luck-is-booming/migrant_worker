import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or safely maintain the environment-configured administrator."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME", "").strip()
        email = os.getenv("ADMIN_EMAIL", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "")
        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING(
                    "ADMIN_USERNAME, ADMIN_EMAIL, or ADMIN_PASSWORD is missing; "
                    "administrator creation was skipped."
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        changed = []
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created administrator {username}."))
            return

        if user.email != email:
            user.email = email
            changed.append("email")
        if not user.is_staff:
            user.is_staff = True
            changed.append("staff status")
        if not user.is_superuser:
            user.is_superuser = True
            changed.append("superuser status")
        if os.getenv("RESET_ADMIN_PASSWORD", "False").lower() == "true":
            user.set_password(password)
            changed.append("password")
        if changed:
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated {username}: {', '.join(changed)}."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"Administrator {username} already exists."))
