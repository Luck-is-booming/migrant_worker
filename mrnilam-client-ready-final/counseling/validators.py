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


def normalize_international_phone(value):
    """Normalize common Nepal/India/international numbers without guessing.

    Explicit international numbers are stored as +<countrycode><number>.
    A Nepal mobile number beginning 97/98 is stored with +977. Ambiguous
    ten-digit Nepal/India values are kept as digits instead of assigning the
    wrong country code; the public forms encourage an explicit country code.
    """
    text = str(value or "").translate(NEPALI_DIGITS).strip()
    if not text:
        raise ValidationError(_("Enter a phone number."))

    has_plus = text.startswith("+")
    digits = re.sub(r"\D", "", text)

    if has_plus:
        if not (8 <= len(digits) <= 15):
            raise ValidationError(
                _("Enter a valid international phone number including the country code.")
            )
        return f"+{digits}"

    if digits.startswith("977") and len(digits) >= 10:
        local = digits[3:]
        if 7 <= len(local) <= 10:
            return f"+977{local.lstrip('0')}"
    if digits.startswith("91") and len(digits) == 12:
        return f"+{digits}"

    local = digits.lstrip("0")
    if not (7 <= len(local) <= 10):
        raise ValidationError(
            _("Enter a valid phone number, preferably with + and the country code.")
        )
    if len(local) == 10 and local.startswith(("97", "98")):
        return f"+977{local}"
    if len(local) == 10 and local[0] in "6789":
        return local
    return local


# Backward-compatible import name used by existing forms.
def normalize_nepal_phone(value):
    return normalize_international_phone(value)


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
    position = upload.tell()
    try:
        if extension == ".pdf":
            # Do not trust the filename or browser-supplied MIME type. A valid
            # PDF begins with the PDF signature; this also rejects renamed
            # executables and ordinary text files.
            if upload.read(5) != b"%PDF-":
                raise ValidationError(_("The uploaded PDF is invalid or corrupted."))
        else:
            image = Image.open(upload)
            image.verify()
    except ValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError(_("The uploaded image is invalid or corrupted.")) from exc
    finally:
        upload.seek(position)
