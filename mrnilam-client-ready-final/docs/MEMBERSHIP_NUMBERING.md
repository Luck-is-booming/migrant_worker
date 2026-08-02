# Membership-number rules

## Scope

Numbers are unique within:

1. Membership category; and
2. Organization unit.

This matches the source records, where the same numeric value may legitimately exist in different district/municipality or General/Life registries.

## Allocation

`MembershipNumberSequence` stores the next number for each scope. The row is locked with PostgreSQL `SELECT ... FOR UPDATE` during allocation. A database uniqueness constraint protects the scope from duplicate sequence rows.

`MembershipNumberIssue` is a permanent ledger of every number ever issued. Its scoped uniqueness constraint is the second protection against racing requests. The ledger remains after a membership is archived or permanently deleted, so numbers are not recycled.

## Stability

- Editing a name, phone, status, address or designation does not change a number.
- An issued number cannot be replaced through ordinary model/admin editing.
- Archive and restore keep the same number.
- Imported explicit numbers are registered in the same permanent ledger.
- Payment approval uses the same allocator.

## Verification

```bash
python manage.py test members.tests.MembershipNumberingTests -v 2
```

For actual simultaneous PostgreSQL requests, use a disposable database:

```bash
TEST_DATABASE_URL='postgresql://...' python manage.py test \
  members.tests.PostgreSQLMembershipNumberConcurrencyTests -v 2
```
