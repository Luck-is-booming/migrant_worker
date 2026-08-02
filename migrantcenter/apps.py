from django.contrib.admin.apps import AdminConfig


class MRNAdminConfig(AdminConfig):
    """Use the MRN Ilam task-focused admin site."""

    default_site = "migrantcenter.admin_site.MRNAdminSite"
