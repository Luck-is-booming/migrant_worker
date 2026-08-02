# Final test report

## Verification completed in the delivery environment

- 129 Python source and migration files parsed successfully with Python 3.13.
- `build.sh` passed `bash -n` shell syntax validation.
- The Nepali catalogue contains 943 active messages with no duplicate, empty, fuzzy, or placeholder-format errors and was compiled to `django.mo` with Babel.
- Public template and Python translation-string extraction found no missing active Nepali message.
- 32 Django templates passed a static block-tag balance check.
- All nine literal template static-file references resolve to included assets.
- Static discovery found no duplicate logical paths.
- JavaScript passed `node --check`; CSS braces are balanced.
- No Git conflict markers were found.
- The project contains one `manage.py` and no nested project copy.
- No `.env`, SQLite database, uploaded media, payment QR, backups, import reports, or virtual environment is included.
- The approved existing organization seal is the source for the navigation logo, footer logo, favicons, Apple touch icon, manifest icons, Open Graph image, and maintenance branding.
- The PostgreSQL membership-number migration includes the non-atomic migration fix required to avoid pending-trigger index creation failures.
- The shared form-field partial now loads Django i18n directly, addressing the three reported `translate` template errors.
- The task-focused admin dashboard, role-aware model visibility, hidden legacy registrations, superuser-only audit tools, chairperson photo preview, and public chairperson-photo rendering were verified statically.

## Representative responsive browser checks

A representative page using the production CSS, JavaScript, official seal, Nepali navigation, long Nepali copy, cards, member records, and footer was checked in headless Chromium at:

- 320, 360, 375, 390, and 430 pixels;
- 768, 1024, 1120, and 1121 pixels;
- 1366 and 1440 pixels.

The representative checks found:

- no horizontal document overflow;
- no header identity/action overlap;
- automatic mobile-menu use through 1120 pixels;
- desktop navigation from 1121 pixels without nav overflow;
- mobile drawer contained within the viewport after its transition;
- body scrolling locked while the drawer is open;
- the mobile language switch displayed inside the drawer;
- Escape reliably closed the drawer.

These representative checks supplement but do not replace testing the rendered Django application with production data and real devices.

## Automated Django tests present

The source contains 50 test methods. They cover:

- repeated imports, dry-runs, conflicting numbers, and multiple memberships;
- numeric public directory ordering, mixed active/archived visibility, language-isolated resources, and private-field protection;
- permanent number stability, archive/restore, non-reuse, and duplicate prevention;
- optional PostgreSQL simultaneous allocation;
- payment approval, idempotency, audit, rejection reason, unique transaction reference, invalid images, and authenticated private-media metadata;
- counseling validation, anti-spam, international phone normalization, and invalid attachment rejection;
- draft/expired content visibility and localized article SEO metadata;
- root redirect, privacy/program/membership routes, payment readiness, seed idempotency, and committee import idempotency.

## Environment limitation

The delivery environment could not install the pinned third-party dependencies because its package index exposed no packages. Therefore `python manage.py check`, `migrate`, `makemigrations --check`, `compilemessages`, `test`, and `collectstatic` were not run through Django here. Static verification is not a substitute for runtime verification in the project virtual environment.

Run before deployment:

```bash
python manage.py check
python manage.py migrate
python manage.py makemigrations --check --dry-run
python manage.py compilemessages
python manage.py test -v 2
rm -rf staticfiles
python manage.py collectstatic --noinput
```

## External verification still required

- real rendered English and Nepali pages with current production data;
- one controlled counseling and contact submission;
- one complete membership/payment review including repeat approval;
- Cloudinary create/read/delete permission for private files;
- Resend verified sender and delivery when notifications are enabled;
- physical-device checks on representative Android, iPhone, tablet, and laptop screens.
