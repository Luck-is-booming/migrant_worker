from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import OrganizationInfo


@receiver([post_save, post_delete], sender=OrganizationInfo)
def clear_public_organization_cache(**kwargs):
    """Ensure staff edits appear publicly without waiting for cache expiry."""
    cache.delete("public-organization-info")
