# Membership migration, import, backup, and rollback

## Safe model transition

The existing `members.Member` table is preserved as a **legacy audit and compatibility table**. Migration `members.0006_normalized_membership_registry` adds the following beside it:

- `Person`: the human being.
- `MembershipCategory`: General, Life, or another verified category.
- `OrganizationUnit`: district, municipality, rural municipality, ward, or another unit.
- `MembershipRecord`: one membership relationship. A person may have any number of memberships.
- `ImportBatch`: source file, checksum, sheet, options, dates, and summary.
- `ImportRowRecord`: original row JSON, normalized row JSON, warnings/errors, and links to affected records.
- `PotentialDuplicate`: cautious staff review rather than automatic same-name merging.

The migration backfills every existing legacy member. It does not delete the legacy row. An exact normalized phone plus a strong name match can connect two legacy rows to one person. A conflicting phone/name combination remains separate and is flagged.

## Production protection sequence

1. Export/backup the production database through Neon before deployment.
2. Deploy code with the new nullable/additive tables and fields.
3. Run `python manage.py migrate --noinput` through `build.sh`.
4. Open Django admin and compare normalized counts with legacy counts.
5. Run both source workbook imports first with `--dry-run` and CSV reports.
6. Review failed rows, non-data rows, and potential duplicates.
7. Run real imports only after the reports reconcile.
8. Keep the legacy table and backup until staff sign off.

Never delete the production database, delete migration history, run `flush`, or use a reset script.

## Commands

List workbook sheets:

```bash
python manage.py import_members "data/membership_sources/Life Time Member of MRN District.xlsm" --list-sheets
```

District dry run:

```bash
python manage.py import_members \
  "data/membership_sources/Life Time Member of MRN District.xlsm" \
  --sheet Sheet1 \
  --level district \
  --unit-name "Ilam District" \
  --dry-run \
  --report import_reports/district-dry-run.csv
```

Municipality dry run:

```bash
python manage.py import_members \
  "data/membership_sources/MRN Ilam nagar level all Member List.xlsm" \
  --sheet Sheet1 \
  --level municipality \
  --unit-name "Ilam Municipality" \
  --dry-run \
  --report import_reports/municipality-dry-run.csv
```

Real import after review:

```bash
python manage.py import_members "data/membership_sources/Life Time Member of MRN District.xlsm" \
  --level district --unit-name "Ilam District" \
  --report import_reports/district-final.csv

python manage.py import_members "data/membership_sources/MRN Ilam nagar level all Member List.xlsm" \
  --level municipality --unit-name "Ilam Municipality" \
  --report import_reports/municipality-final.csv
```

Use `--update-existing` only after reviewing the dry-run report. A real import automatically writes a JSON backup before changing records.

Phakphokthum DOCX dry run and import:

```bash
python manage.py import_phakphokthum_committee --dry-run --report import_reports/phakphokthum-dry-run.csv
python manage.py import_phakphokthum_committee --report import_reports/phakphokthum-final.csv
```

The DOCX does not state membership category or numbers. The command defaults to General Member and uses the serial number. Confirm this business decision before production use.

## Batch rollback

```bash
python manage.py rollback_member_import <IMPORT_BATCH_UUID>
```

Rollback affects only records created by that batch or restores fields captured before that batch. It does not delete pre-existing unrelated people or memberships. Always keep the generated pre-import backup and test rollback on a copied database first.

## Current source reconciliation

| Metric | Value |
|---|---:|
| Total workbook rows | 278 |
| Title/header rows | 6 |
| Blank rows | 3 |
| Non-data/summary rows | 1 |
| Valid membership rows | 268 |
| Life memberships | 70 |
| General memberships | 198 |
| Blank phone rows | 114 |
| Blank membership numbers among valid rows | 0 |
| Strong same-person/multiple-membership candidates | 2 |
| Contradictory-phone duplicate-review groups | 2 |
| Expected people in an empty normalized registry | 266 |
| Expected memberships in an empty normalized registry | 268 |
| Records deleted | 0 |

The two strong multiple-membership candidates are Nabin and Jyoti. Exact details are in `audit_reports/multiple-membership-candidates.csv`. Contradictory shared-phone rows are in `audit_reports/potential-duplicate-review.csv`. This is a source audit, not a claim about the live database after migration.
