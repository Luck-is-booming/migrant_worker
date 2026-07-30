import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates the production superuser if it does not already exist."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME", "").strip()
        email = os.getenv("ADMIN_EMAIL", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Admin environment variables are incomplete; "
                    "skipping administrator creation."
                )
            )
            return

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed_fields = []

        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.email = email
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created administrator: {username}"
                )
            )
            return

        if not user.is_staff:
            user.is_staff = True
            changed_fields.append("is_staff")

        if not user.is_superuser:
            user.is_superuser = True
            changed_fields.append("is_superuser")

        if email and user.email != email:
            user.email = email
            changed_fields.append("email")

        # Password is not reset on every deployment.
        # Set RESET_ADMIN_PASSWORD=True only when intentionally resetting it.
        reset_password = (
            os.getenv("RESET_ADMIN_PASSWORD", "False") == "True"
        )

        if reset_password:
            user.set_password(password)
            changed_fields.append("password")

        if changed_fields:
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated administrator: {username}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Administrator already exists: {username}"
                )
            )