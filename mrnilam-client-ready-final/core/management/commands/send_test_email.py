from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send one test email using the currently configured Django email backend."

    def add_arguments(self, parser):
        parser.add_argument("--to", required=True, help="Recipient email address")

    def handle(self, *args, **options):
        recipient = options["to"].strip()
        if not recipient:
            raise CommandError("Provide a recipient with --to.")

        sent = send_mail(
            subject="MRN Ilam email test",
            message=(
                "This is a test email from the MRN Ilam Django project.\n\n"
                f"Configured sender: {settings.DEFAULT_FROM_EMAIL}\n"
                f"Backend: {settings.EMAIL_BACKEND}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

        if sent != 1:
            raise CommandError("Django did not report a successful email send.")

        self.stdout.write(self.style.SUCCESS(f"Test email sent to {recipient}."))
