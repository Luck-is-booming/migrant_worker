"""Concurrency-safe membership-number allocation and issuance history.

Membership numbers are scoped by membership category and organization unit.
The source workbooks legitimately reuse values in different scopes, so a
number such as ``4`` can exist for both a district Life Membership and a
municipality Life Membership. Within a scope, however, a number is issued only
once and is never silently recycled after archival or deletion.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Max


def _scope_filter(category_id: int, organization_unit_id: int) -> dict:
    if not category_id or not organization_unit_id:
        raise ValidationError(
            "Membership category and organization unit are required before "
            "a membership number can be issued."
        )
    return {
        "category_id": category_id,
        "organization_unit_id": organization_unit_id,
    }


def _locked_sequence(*, scope, default_next=1):
    """Return a locked sequence row without leaving a broken transaction.

    Concurrent ``get_or_create`` calls can race on PostgreSQL. The potentially
    failing insert runs inside a nested savepoint so an ``IntegrityError`` can
    be recovered from safely inside the surrounding allocation transaction.
    """

    from .models import MembershipNumberSequence

    try:
        with transaction.atomic():
            sequence, created = (
                MembershipNumberSequence.objects.select_for_update().get_or_create(
                    **scope,
                    defaults={"next_number": max(1, default_next)},
                )
            )
    except IntegrityError:
        sequence = MembershipNumberSequence.objects.select_for_update().get(**scope)
        created = False
    return sequence, created


def allocate_membership_number(
    *,
    category_id: int,
    organization_unit_id: int,
    issued_by=None,
    source: str = "system",
):
    """Reserve and return the next numeric membership number for a scope.

    The sequence row is locked with ``select_for_update``. The issuance ledger
    also has a database uniqueness constraint, providing a second line of
    defense when simultaneous requests race to allocate a number.
    """

    from .models import MembershipNumberIssue, MembershipRecord

    scope = _scope_filter(category_id, organization_unit_id)
    with transaction.atomic():
        sequence, created = _locked_sequence(scope=scope)

        if created or sequence.next_number < 1:
            highest_record = (
                MembershipRecord.objects.filter(**scope).aggregate(
                    value=Max("membership_number_int")
                )["value"]
                or 0
            )
            highest_issue = (
                MembershipNumberIssue.objects.filter(**scope).aggregate(
                    value=Max("number_int")
                )["value"]
                or 0
            )
            sequence.next_number = max(highest_record, highest_issue) + 1

        while True:
            candidate = sequence.next_number
            normalized = str(candidate)
            try:
                # Use a savepoint: a uniqueness race must not poison the outer
                # transaction before we advance to the next candidate.
                with transaction.atomic():
                    issue = MembershipNumberIssue.objects.create(
                        **scope,
                        membership_number=normalized,
                        membership_number_normalized=normalized,
                        number_int=candidate,
                        source=source[:30],
                        issued_by=issued_by,
                    )
            except IntegrityError:
                sequence.next_number += 1
                continue
            break

        sequence.next_number = candidate + 1
        sequence.save(update_fields=["next_number", "updated_at"])
        return normalized, issue


def register_membership_number(*, membership, source: str = "existing", issued_by=None):
    """Record an explicitly supplied number and advance its sequence safely."""

    from .models import MembershipNumberIssue

    normalized = membership.membership_number_normalized
    if not normalized:
        return None

    scope = _scope_filter(membership.category_id, membership.organization_unit_id)
    with transaction.atomic():
        defaults = {
            "membership_number": membership.membership_number,
            "number_int": membership.membership_number_int,
            "membership": membership,
            "source": source[:30],
            "issued_by": issued_by,
        }
        try:
            with transaction.atomic():
                issue, created = (
                    MembershipNumberIssue.objects.select_for_update().get_or_create(
                        **scope,
                        membership_number_normalized=normalized,
                        defaults=defaults,
                    )
                )
        except IntegrityError:
            issue = MembershipNumberIssue.objects.select_for_update().get(
                **scope,
                membership_number_normalized=normalized,
            )
            created = False

        if not created:
            if issue.membership_id not in {None, membership.pk}:
                raise ValidationError(
                    "This membership number was already issued in the selected "
                    "category and organization unit."
                )
            changed = []
            if issue.membership_id is None:
                issue.membership = membership
                changed.append("membership")
            if issue.membership_number != membership.membership_number:
                issue.membership_number = membership.membership_number
                changed.append("membership_number")
            if issue.number_int != membership.membership_number_int:
                issue.number_int = membership.membership_number_int
                changed.append("number_int")
            if changed:
                issue.save(update_fields=changed)

        if membership.membership_number_int is not None:
            sequence, _ = _locked_sequence(
                scope=scope,
                default_next=membership.membership_number_int + 1,
            )
            minimum_next = membership.membership_number_int + 1
            if sequence.next_number < minimum_next:
                sequence.next_number = minimum_next
                sequence.save(update_fields=["next_number", "updated_at"])
        return issue
