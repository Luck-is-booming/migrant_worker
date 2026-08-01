# Final self-audit

## Completed in the repository

- Existing data tables and historical migrations are preserved.
- Normalized Person-to-many-Membership architecture is additive.
- Legacy members are backfilled without deletion.
- Imports are path-based, rerunnable, transactional, dry-runnable, reportable, backed up, and traceable by file/sheet/checksum/row.
- Imports never delete records absent from a source file.
- Ambiguous identity matches are separated and flagged.
- Counseling is the primary public action and requires a valid Nepal phone plus consent.
- Private counseling and payment records are excluded from public URLs and sitemaps.
- Sensitive upload filenames are randomized and staff links are protected by admin permissions.
- Public pages do not render phone/email/payment/internal fields from the member registry.
- Publishing supports draft, published, and archived states.
- Public navigation, SEO metadata, bilingual URLs, robots, sitemaps, 404/500 pages, and a database health check are included.
- Free-Render build configuration applies committed migrations but does not run membership imports.
- Least-privilege groups are created through a management command.
- Destructive reset code, public admin creation, CDN Tailwind, raw SVG rendering, and duplicate payment templates are removed.
- Public fallback content contains no invented people, contacts, achievements, partnerships, statistics, or alerts.

## Static verification executed here

- Every Python file compiled with `python -m compileall`.
- Every Python file parsed successfully with `ast.parse`.
- `build.sh` passed `bash -n` syntax validation.
- Workbook and DOCX source files were parsed directly for audit reports.
- Nepali message catalog compiled successfully with Babel.

## Verification that still must run in the user's Django environment

This execution environment does not contain Django and could not run the application. Before production deployment, run:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
python manage.py collectstatic --noinput
```

Then run both source imports with `--dry-run` against a copied production database and reconcile the CSV reports before any real import.

## Production facts not available for verification

- Current Neon/PostgreSQL row counts and duplicate state.
- Cloudinary account-level private/authenticated delivery capabilities.
- Current real staff accounts and permissions.
- Approved organization name, registration details, office contacts, service hours, emergency resources, payment purpose, and privacy-retention period.
- Final human-approved English spelling of personal names.

No claim of a perfect production import is made until the live totals reconcile and `Records deleted` remains zero.
