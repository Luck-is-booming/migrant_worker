from django.core.management.base import BaseCommand, CommandError

from members.importing import ImportValidationError, rollback_import_batch
from members.models import ImportBatch


class Command(BaseCommand):
    help = "Rollback only the changes recorded by one member import batch."

    def add_arguments(self, parser):
        parser.add_argument("batch_id", help="Import batch UUID.")
        parser.add_argument("--confirm", action="store_true", help="Required confirmation flag.")

    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError("Add --confirm after reviewing the batch and backup.")
        try:
            batch = ImportBatch.objects.get(public_id=options["batch_id"])
        except ImportBatch.DoesNotExist as exc:
            raise CommandError("Import batch not found.") from exc
        try:
            rollback_import_batch(batch)
        except ImportValidationError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Rolled back import batch {batch.public_id}."))
