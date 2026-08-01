import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from django.db import transaction
from django.db.models import Q

from .models import (
    MembershipCategory,
    MembershipRecord,
    OrganizationUnit,
    Person,
    PotentialDuplicate,
    normalize_person_name,
)
from .name_utils import romanize_nepali_name


NEPALI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
NAME_NOISE = {"रकम", "श्री", "mr", "mrs", "ms"}


def normalize_phone(value):
    text = str(value or "").translate(NEPALI_DIGITS)
    digits = re.sub(r"\D", "", text)
    if digits.startswith("977") and len(digits) >= 12:
        digits = digits[3:]
    return digits


def comparable_name(value):
    words = [
        word
        for word in re.split(r"\s+", str(value or "").strip().casefold())
        if word and word not in NAME_NOISE
    ]
    return normalize_person_name(" ".join(words))


def names_are_strong_match(left, right, threshold=0.76):
    a = comparable_name(left)
    b = comparable_name(right)
    if not a or not b:
        return False
    if a == b or a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= threshold


def get_or_create_category(code):
    defaults = {
        "life": {
            "name_ne": "आजीवन सदस्य",
            "name_en": "Life Member",
            "display_order": 1,
        },
        "general": {
            "name_ne": "साधारण सदस्य",
            "name_en": "General Member",
            "display_order": 2,
        },
    }
    values = defaults.get(
        code,
        {
            "name_ne": code.replace("-", " ").title(),
            "name_en": code.replace("-", " ").title(),
            "display_order": 50,
        },
    )
    category, _ = MembershipCategory.objects.get_or_create(code=code, defaults=values)
    return category


def get_or_create_unit(level, name_en, name_ne=""):
    clean_name = str(name_en or "Unknown Unit").strip()
    unit, created = OrganizationUnit.objects.get_or_create(
        level=level or "unknown",
        name_en=clean_name,
        defaults={"name_ne": str(name_ne or "").strip()},
    )
    if not created and name_ne and not unit.name_ne:
        unit.name_ne = str(name_ne).strip()
        unit.save(update_fields=["name_ne"])
    return unit


@dataclass
class IdentityResolution:
    person: Person
    created: bool
    warnings: list
    duplicate_candidates: list


def resolve_person_identity(*, name_ne, name_en="", phone="", location=""):
    """Resolve only when identity signals are strong.

    A repeated name alone never causes a merge. An exact normalized phone plus a
    strong name match may link two memberships to one person. Contradictory
    phone matches are retained as separate people and flagged for review.
    """

    normalized_phone = normalize_phone(phone)
    warnings = []
    duplicate_candidates = []

    if normalized_phone:
        candidates = list(Person.objects.filter(phone=normalized_phone))
        strong = [p for p in candidates if names_are_strong_match(name_ne, p.name_ne)]
        if len(strong) == 1:
            person = strong[0]
            changed = False
            if name_en and not person.name_en:
                person.name_en = name_en
                changed = True
            if location and not person.location:
                person.location = location
                changed = True
            if changed:
                person.save()
            return IdentityResolution(person, False, warnings, candidates)
        if candidates:
            warnings.append(
                "The phone number matches another person but the names do not "
                "match strongly; records were kept separate for manual review."
            )
            duplicate_candidates.extend(candidates)

    person = Person.objects.create(
        name_ne=str(name_ne or "").strip(),
        name_en=str(name_en or "").strip() or romanize_nepali_name(name_ne),
        phone=normalized_phone,
        location=str(location or "").strip(),
        needs_identity_review=bool(duplicate_candidates),
    )

    for candidate in duplicate_candidates:
        left, right = sorted([person, candidate], key=lambda value: value.pk)
        PotentialDuplicate.objects.get_or_create(
            person_a=left,
            person_b=right,
            defaults={
                "signals": {
                    "same_phone": normalized_phone,
                    "name_a": left.name_ne,
                    "name_b": right.name_ne,
                }
            },
        )

    return IdentityResolution(person, True, warnings, duplicate_candidates)


def sync_legacy_member(legacy_member):
    """Create/update the normalized membership without deleting legacy data."""

    category = get_or_create_category(legacy_member.membership_type or "general")
    unit = get_or_create_unit(
        legacy_member.level or "unknown",
        legacy_member.unit_name or legacy_member.municipality or "Unknown Unit",
    )

    existing = MembershipRecord.objects.filter(legacy_member=legacy_member).select_related("person").first()
    if existing:
        person = existing.person
        if legacy_member.name_ne:
            person.name_ne = legacy_member.name_ne
        if legacy_member.name_en:
            person.name_en = legacy_member.name_en
        if legacy_member.phone and not person.phone:
            person.phone = normalize_phone(legacy_member.phone)
        if legacy_member.address and not person.location:
            person.location = legacy_member.address
        person.save()
        record = existing
    else:
        resolution = resolve_person_identity(
            name_ne=legacy_member.name_ne,
            name_en=legacy_member.name_en,
            phone=legacy_member.phone,
            location=legacy_member.address or legacy_member.municipality,
        )
        person = resolution.person
        record = MembershipRecord(person=person, legacy_member=legacy_member)

    record.category = category
    record.organization_unit = unit
    record.membership_number = legacy_member.membership_number
    record.status = legacy_member.status or "unknown"
    record.designation = legacy_member.designation
    record.destination_country = legacy_member.destination_country
    record.address_display = legacy_member.address or legacy_member.municipality
    record.is_public = legacy_member.is_public and person.is_public
    record.source_application = legacy_member.source_membership
    record.save()
    return record


def sync_all_legacy_members(queryset=None):
    queryset = queryset or Member.objects.all()
    with transaction.atomic():
        return [sync_legacy_member(member) for member in queryset.iterator()]


# Imported late to avoid a circular import in type checking and app loading.
from .models import Member  # noqa: E402  pylint: disable=wrong-import-position


def merge_people(*, canonical, duplicate, reviewed_by=None):
    """Transactionally move memberships while preserving the duplicate person row.

    A merge is rejected when it would create two memberships with the same
    category, organization unit and membership number. The duplicate Person is
    archived through merged_into rather than physically deleted.
    """

    if canonical.pk == duplicate.pk:
        raise ValueError("A person cannot be merged into itself.")

    with transaction.atomic():
        canonical = Person.objects.select_for_update().get(pk=canonical.pk)
        duplicate = Person.objects.select_for_update().get(pk=duplicate.pk)

        for membership in duplicate.memberships.select_for_update():
            conflict = MembershipRecord.objects.filter(
                person=canonical,
                category=membership.category,
                organization_unit=membership.organization_unit,
                membership_number_normalized=membership.membership_number_normalized,
            ).exclude(pk=membership.pk).exists()
            if conflict:
                raise ValueError(
                    "Merge would create a conflicting membership. Review membership "
                    "numbers and units before merging."
                )
            membership.person = canonical
            membership.save(update_fields=["person", "updated_at"])

        if not canonical.phone and duplicate.phone:
            canonical.phone = duplicate.phone
        if not canonical.email and duplicate.email:
            canonical.email = duplicate.email
        if not canonical.name_en and duplicate.name_en:
            canonical.name_en = duplicate.name_en
        canonical.needs_identity_review = False
        canonical.save()

        duplicate.is_public = False
        duplicate.needs_identity_review = False
        duplicate.merged_into = canonical
        duplicate.save(update_fields=["is_public", "needs_identity_review", "merged_into", "updated_at"])

        for review in PotentialDuplicate.objects.filter(
            Q(person_a__in=[canonical, duplicate]) | Q(person_b__in=[canonical, duplicate])
        ):
            review.status = "same" if {review.person_a_id, review.person_b_id} == {canonical.pk, duplicate.pk} else review.status
            if review.status == "same":
                review.reviewed_by = reviewed_by
                from django.utils import timezone

                review.reviewed_at = timezone.now()
                review.save(update_fields=["status", "reviewed_by", "reviewed_at"])

    return canonical
