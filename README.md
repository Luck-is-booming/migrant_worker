# MRN Ilam — client-ready bilingual NGO platform

MRN Ilam is a Django platform for foreign-employment awareness, private counseling, verified resources, organizational publishing, membership management, and optional manual membership-payment verification.

The public wording deliberately presents the organization as an information, awareness, counseling, and referral service. It does **not** claim to issue visas, recruit workers, guarantee jobs, or guarantee migration outcomes.

## Main capabilities

- Fully localized `/en/` and `/ne/` public routes with canonical and alternate-language metadata.
- Private counseling and contact workflows with consent, server-side validation, anti-spam controls, staff notes, and protected attachments.
- Normalized member registry: one `Person` may hold multiple separate `MembershipRecord` rows.
- Permanent, concurrency-safe membership numbers scoped by membership category and organization unit.
- Repeatable Excel imports with dry-run, row reports, duplicate warnings, transactions, and pre-import backups.
- Public member search, filters, pagination, privacy-safe fields, and numeric ordering (`2` before `10`).
- Manual QR-payment workflow with authenticated private evidence, unique transaction references, approval audit, and idempotent member creation.
- Bilingual news, notices, safety alerts, programs, official resources, FAQ, privacy, and disclaimer pages.
- Least-privilege admin roles for content, membership, counseling, and payment staff.
- Render, Neon PostgreSQL, WhiteNoise, Cloudinary, Resend, health-check, and secure production settings.

## Technology

- Python 3.12+ (Render is pinned to Python 3.13.5)
- Django 6.0
- PostgreSQL in production; SQLite for ordinary local development/tests
- Django templates and first-party CSS/JavaScript
- Cloudinary-compatible media storage
- Resend through django-anymail
- Gunicorn and WhiteNoise

## Local installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Use at least these local values:

```env
DEBUG=True
USE_SQLITE=True
SECRET_KEY=replace-this-local-secret
EMAIL_NOTIFICATIONS_ENABLED=False
COUNSELING_ATTACHMENTS_ENABLED=False
SITE_URL=http://127.0.0.1:8000
```

Initialize:

```bash
python manage.py check
python manage.py migrate
python manage.py setup_staff_groups
python manage.py createsuperuser
python manage.py seed_launch_content
python manage.py collectstatic --noinput
python manage.py test
python manage.py runserver
```

Open:

- `http://127.0.0.1:8000/en/`
- `http://127.0.0.1:8000/ne/`
- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/health/`

## Official membership payment setup

The project intentionally ships **without a payment QR and with unpublished fees**. This prevents an unverified personal QR or guessed fee from appearing publicly.

In Django Admin, open **Core → Membership payment settings** and enter:

1. Verified General Membership fee.
2. Verified Life Membership fee.
3. Exact recipient name shown by the payment app.
4. Official QR image supplied or approved by the organization.
5. English and Nepali account details/instructions.
6. Scan the uploaded QR on two devices and confirm the recipient.
7. Enable the configuration only after all checks pass.

Until then, the public application button remains safely paused. See `docs/CLIENT_ADMIN_GUIDE.md`.

## Member imports

Read `docs/MEMBER_IMPORT.md` before importing. Always run a dry-run and review the report first.

District Life Members:

```bash
python manage.py import_members \
  "data/membership_sources/Life Time Member of MRN District.xlsm" \
  --level district \
  --unit-name "Ilam District" \
  --dry-run \
  --report import_reports/district-dry-run.csv
```

Ilam Municipality members:

```bash
python manage.py import_members \
  "data/membership_sources/MRN Ilam nagar level all Member List.xlsm" \
  --level municipality \
  --unit-name "Ilam Municipality" \
  --dry-run \
  --report import_reports/municipality-dry-run.csv
```

Phakphokthum committee:

```bash
python manage.py import_phakphokthum_committee \
  --dry-run \
  --report import_reports/phakphokthum-dry-run.csv
```

District executive committee/public leadership draft:

```bash
python manage.py import_district_executive_committee \
  --dry-run \
  --report import_reports/district-committee-dry-run.csv
```

Remove `--dry-run` only after review. Re-running an unchanged source is idempotent; it does not delete missing rows.

## Registry export

```bash
python manage.py export_member_registry exports/members.csv
python manage.py export_member_registry exports/members-private.json \
  --format json --include-private-contact
```

Treat private exports as confidential and store them outside Git.

## Translation workflow

```bash
python manage.py makemessages -l ne
# Review locale/ne/LC_MESSAGES/django.po
python manage.py compilemessages
python manage.py test
```

Do not publish machine-generated Nepali without a human review. Admin content has separate English and Nepali fields where public bilingual content is required.

## Testing

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

The default suite uses in-memory SQLite. To verify simultaneous membership-number allocation on PostgreSQL, provide a disposable database:

```bash
TEST_DATABASE_URL='postgresql://...' python manage.py test \
  members.tests.PostgreSQLMembershipNumberConcurrencyTests -v 2
```

Never point `TEST_DATABASE_URL` at production.

## Render deployment

Build command:

```bash
bash build.sh
```

Start command:

```bash
gunicorn migrantcenter.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 90
```

Minimum production variables:

```env
DEBUG=False
USE_SQLITE=False
SECRET_KEY=...
DATABASE_URL=...
ALLOWED_HOSTS=mrnilam.org.np,www.mrnilam.org.np,<service>.onrender.com
CSRF_TRUSTED_ORIGINS=https://mrnilam.org.np,https://www.mrnilam.org.np,https://<service>.onrender.com
SITE_URL=https://mrnilam.org.np
CLOUDINARY_URL=...
ADMIN_USERNAME=...
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
RESET_ADMIN_PASSWORD=False
EMAIL_NOTIFICATIONS_ENABLED=False
HSTS_ENABLED=False
```

Enable email only after verifying the Resend sender. Enable HSTS only after HTTPS is stable for the apex domain and all intended subdomains.

`build.sh` never imports members, seeds articles, overwrites content, or resets an existing admin password unless `RESET_ADMIN_PASSWORD=True` is deliberately set.

## Private media and Cloudinary

Public article/leadership images use the configured default Cloudinary media storage. New counseling attachments and payment evidence use Cloudinary's authenticated delivery type through `core.storage.AuthenticatedCloudinaryStorage`; the database stores resource metadata and staff access uses a five-minute signed URL behind permission-checked Django views. Local development and automated tests use ordinary local/default storage.

Production verification must confirm that the Cloudinary credentials can create, read and delete authenticated assets. Older deployments may still contain legacy public Cloudinary object names; authorized staff can read them for migration, and `python manage.py audit_launch_readiness` reports how many need replacement/re-upload.

## Launch readiness

```bash
python manage.py audit_launch_readiness
```

The command reports missing verified organization contacts, payment setup, public resources/articles, and unresolved duplicate reviews without changing data.

## Documentation

- `docs/ARCHITECTURE.md`
- `docs/MEMBERSHIP_NUMBERING.md`
- `docs/MEMBER_IMPORT.md`
- `docs/CLIENT_ADMIN_GUIDE.md`
- `docs/ADMIN_OPERATIONS_GUIDE.md`
- `docs/CLIENT_HANDOVER_OVERVIEW.md`
- `docs/EXTERNAL_CONFIGURATION_REQUIRED.md`
- `docs/LOCAL_SETUP_AND_PACKAGING.md`
- `docs/DEPLOYMENT_AND_ROLLBACK.md`
- `docs/LAUNCH_CHECKLIST.md`
- `docs/FINAL_TEST_REPORT.md`
- `CHANGELOG.md`
