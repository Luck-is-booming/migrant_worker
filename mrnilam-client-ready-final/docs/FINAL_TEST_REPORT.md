# Final test report

## Verification completed in the delivery environment

- 124 Python source/migration files parsed and compiled successfully with Python 3.13.
- Both shell scripts passed `bash -n`.
- The Nepali catalogue contains 596 translated messages, no empty/fuzzy entries, and compiled to `django.mo` with Babel.
- Public Python/template translation-string extraction found complete Nepali catalogue coverage.
- No Git conflict markers were found.
- No `.env`, SQLite database, uploaded media, payment QR, backups, import reports or virtual environment is included.
- Source Excel workbooks and the committee DOCX were opened and structurally inspected.
- 39 application migration files and their local dependency ordering were statically inspected.
- The personal/static payment QR from the uploaded project was removed.

## Automated Django tests added or updated

The source contains 50 test methods. They require the installed Django dependencies to execute.

Tests cover:

- repeated imports, dry-runs, conflicting numbers and multiple memberships;
- numeric public directory ordering, mixed active/archived visibility, language-isolated resources and private-field protection;
- permanent number stability, archive/restore with public-visibility preservation, non-reuse and duplicate prevention;
- optional PostgreSQL simultaneous allocation;
- payment approval, idempotency, audit, rejection reason, unique transaction reference, invalid image and authenticated private-media metadata;
- counseling validation, anti-spam, international phone normalization and renamed/invalid PDF rejection;
- draft/expired content visibility and localized article SEO metadata;
- root redirect, privacy/program/membership routes, payment readiness, content seed idempotency and committee import idempotency.

## Environment limitation

The delivery sandbox could not install the pinned third-party dependencies because its package index exposed no packages. Therefore `python manage.py test`, `migrate`, `makemigrations --check`, `collectstatic` and real Cloudinary/Resend/Neon operations were **not** executed in that sandbox. Static checks are not a substitute for the recipient’s runtime verification.

Run this before deployment:

```bash
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

## External verification still required

- Official organization identity and contact facts
- Official General/Life fees
- Official QR and payment recipient
- Cloudinary create/read permissions and protected evidence access
- Resend verified sender and delivery
- Neon backup/restore procedure
- Human review of English leadership spellings and all public Nepali content
- Physical-device responsive/accessibility checks
