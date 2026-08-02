# Member import and reconciliation

## Safety rules

1. Back up the target database.
2. Run `--dry-run` and open the CSV report.
3. Confirm valid, warning, failed and deleted counts.
4. Review likely duplicate people; do not merge based on name alone.
5. Run the real import once.
6. Re-run in dry mode and confirm no uncontrolled creation.
7. Export and sample the destination registry.

Real imports create a pre-import JSON backup. Imports use transactions, preserve source-row audit data, normalize whitespace and phone values conservatively, and never delete destination records absent from a file.

## Spreadsheet mapping

The importer detects common Nepali/English headers for serial number, name, address, designation, membership number, date, membership type, destination country, phone and status/remarks. Name, membership type, organizational scope and a usable source identity are required for an official membership. Optional blank contact fields are retained as blank.

## Commands

See the exact commands in the root README. Reports and backups are ignored by Git because they may contain personal information.

## Status rule

An existing authoritative membership roster is treated as Active when its status cell is blank and no source evidence indicates otherwise. Explicit inactive, pending, expired, suspended, archived or rejected values are preserved.

## Duplicate rule

- Matching verified phone plus compatible identity evidence may resolve to the same person.
- Name alone never silently merges people.
- Multiple memberships for one person are retained as separate records.
- Conflicting use of one number inside the same registry scope is reported and rolled back rather than overwritten.
