from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Register lightweight cache invalidation only; no business workflows use signals.
        from . import signals  # noqa: F401
