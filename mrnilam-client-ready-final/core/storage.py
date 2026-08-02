"""Storage helpers for public and sensitive uploaded files.

Public content continues to use the configured default media storage. Counseling
attachments and payment evidence use authenticated Cloudinary delivery when
Cloudinary is configured. Their URLs are generated as short-lived signed API
links and are exposed only through permission-protected admin views.
"""

from __future__ import annotations

import time
from pathlib import Path
from urllib.request import urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage, storages
from django.core.files.uploadedfile import UploadedFile
from django.utils.deconstruct import deconstructible


@deconstructible
class AuthenticatedCloudinaryStorage(Storage):
    """Cloudinary storage using the ``authenticated`` delivery type.

    The database value contains only resource metadata, never a reusable public
    URL. ``url()`` creates a signed download URL that expires after five minutes.
    """

    marker = "authenticated"
    expiry_seconds = 5 * 60

    @staticmethod
    def _resource_type(filename):
        return "raw" if Path(filename).suffix.casefold() == ".pdf" else "image"

    @classmethod
    def _pack(cls, *, public_id, resource_type, format_name):
        safe_format = str(format_name or "bin").strip("./") or "bin"
        return f"{cls.marker}/{resource_type}/{safe_format}/{public_id}"

    @classmethod
    def is_authenticated_name(cls, name):
        return str(name or "").startswith(f"{cls.marker}/")

    @classmethod
    def _unpack(cls, name):
        parts = str(name or "").split("/", 3)
        if len(parts) != 4 or parts[0] != cls.marker:
            raise ValueError("Invalid authenticated Cloudinary storage name.")
        _, resource_type, format_name, public_id = parts
        if resource_type not in {"image", "raw"} or not public_id:
            raise ValueError("Invalid authenticated Cloudinary resource metadata.")
        return public_id, resource_type, format_name

    def _save(self, name, content):
        import cloudinary.uploader

        normalized = str(name).replace("\\", "/").lstrip("/")
        resource_type = self._resource_type(normalized)
        source = UploadedFile(content, name=Path(normalized).name)
        path = Path(normalized)
        options = {
            "resource_type": resource_type,
            "type": "authenticated",
            "public_id": path.stem,
            "overwrite": False,
            "unique_filename": False,
            "invalidate": True,
        }
        folder = str(path.parent).replace(".", "").strip("/")
        if folder:
            options["folder"] = folder
        response = cloudinary.uploader.upload(source, **options)
        return self._pack(
            public_id=response["public_id"],
            resource_type=response.get("resource_type", resource_type),
            format_name=response.get("format") or path.suffix.lstrip(".") or "bin",
        )

    def _signed_url(self, name, *, attachment=False):
        from cloudinary.utils import private_download_url

        public_id, resource_type, format_name = self._unpack(name)
        return private_download_url(
            public_id,
            format_name,
            type="authenticated",
            resource_type=resource_type,
            attachment=attachment,
            expires_at=int(time.time()) + self.expiry_seconds,
        )

    @staticmethod
    def _legacy_storage():
        # Existing installations may have older public Cloudinary object names.
        # Keep those records readable for authorized staff; new uploads always
        # use authenticated delivery and the launch audit reports legacy names.
        from cloudinary_storage.storage import MediaCloudinaryStorage

        return MediaCloudinaryStorage()

    def _open(self, name, mode="rb"):
        if "r" not in mode:
            raise ValueError("Authenticated media can only be opened for reading.")
        if not self.is_authenticated_name(name):
            return self._legacy_storage().open(name, mode)
        with urlopen(self._signed_url(name), timeout=30) as response:  # nosec B310 - signed Cloudinary URL generated server-side
            content = ContentFile(response.read(), name=Path(name).name)
        content.mode = mode
        return content

    def url(self, name):
        if not self.is_authenticated_name(name):
            return self._legacy_storage().url(name)
        return self._signed_url(name)

    def delete(self, name):
        import cloudinary.uploader

        if not self.is_authenticated_name(name):
            return self._legacy_storage().delete(name)
        public_id, resource_type, _ = self._unpack(name)
        result = cloudinary.uploader.destroy(
            public_id,
            type="authenticated",
            resource_type=resource_type,
            invalidate=True,
        )
        return result.get("result") in {"ok", "not found"}

    def exists(self, name):
        # Upload paths contain UUIDs. Avoid an API round-trip for every save;
        # Cloudinary is also configured with overwrite=False.
        return False

    def get_available_name(self, name, max_length=None):
        normalized = str(name).replace("\\", "/")
        return normalized[:max_length] if max_length else normalized


def get_private_media_storage():
    """Return authenticated cloud storage in production, default storage otherwise."""

    cloudinary_url = getattr(settings, "CLOUDINARY_URL", "")
    if cloudinary_url and not getattr(settings, "IS_TESTING", False):
        return AuthenticatedCloudinaryStorage()
    return storages["default"]
