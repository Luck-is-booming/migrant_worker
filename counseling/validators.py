import re
from pathlib import Path

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError


NEPALI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024


def normalize_nepal_phone(value):
    text = str(value or "").translate(NEPALI_DIGITS).strip()
    digits = re.sub(r"\D", "", text)
    if digits.startswith("977"):
        digits = digits[3:]
    if digits.startswith("0"):
        digits = digits[1:]

    # Nepal mobile numbers are ten local digits beginning 97 or 98. Landline
    # lengths vary, so accept 7–10 digits after removing country/trunk prefixes.
    if not (7 <= len(digits) <= 10):
        raise ValidationError(
            _("Enter a valid Nepal phone number, such as 98XXXXXXXX or +977 98XXXXXXXX.")
        )
    if len(digits) == 10 and not digits.startswith(("97", "98")):
        raise ValidationError(
            _("Ten-digit Nepal mobile numbers normally begin with 97 or 98.")
        )
    return f"+977{digits}"


def validate_private_attachment(upload):
    if not upload:
        return
    if upload.size > MAX_ATTACHMENT_SIZE:
        raise ValidationError(_("The attachment must be 5 MB or smaller."))
    extension = Path(upload.name).suffix.casefold()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(_("Upload only PDF, JPG, PNG, or WebP files."))
    content_type = getattr(upload, "content_type", "")
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(_("The uploaded file type is not allowed."))
    if extension != ".pdf":
        try:
            position = upload.tell()
            image = Image.open(upload)
            image.verify()
            upload.seek(position)
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ValidationError(_("The uploaded image is invalid or corrupted.")) from exc
