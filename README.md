# MRN Ilam

Production-oriented bilingual Django platform for foreign-employment information, awareness, private counseling, official resources, notices, membership management, and optional membership-fee verification.

The organization is positioned as a counseling and awareness body. It does not issue visas, guarantee jobs, recruit workers, or replace government, legal, medical, or financial professionals.

## Apps

- `core`: organization settings, public pages, official resources, FAQ, team, general contact, and membership applications.
- `counseling`: private requests, categories, consent, staff workflow, notes, contact attempts, retention status, spam protection.
- `members`: normalized people and multiple memberships, legacy preservation, public directory, imports, duplicate review.
- `blog`: draft/published/archived news, notices, alerts, events, and counseling updates.
- `payments`: optional membership payment evidence and staff audit workflow. Counseling never requires payment.

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set local `.env`:

```env
DEBUG=True
USE_SQLITE=True
SECRET_KEY=local-development-secret
EMAIL_NOTIFICATIONS_ENABLED=False
COUNSELING_ATTACHMENTS_ENABLED=False
```

Then:

```bash
python manage.py migrate
python manage.py setup_staff_groups
python manage.py createsuperuser
python manage.py check
python manage.py test
python manage.py runserver
```

Local SQLite is used when `USE_SQLITE=True`. Production uses `DATABASE_URL` and `USE_SQLITE=False`.

## Membership import

Read `docs/MEMBERSHIP_MIGRATION_AND_IMPORT.md` before importing anything. Always dry-run and review the CSV report. Real imports create a JSON backup and never delete records missing from the source.

## Email

With no `RESEND_API_KEY`, development uses Django’s console email backend. Production notifications are optional and workflows still save if notification delivery fails. Staff notification emails do not include full counseling messages or phone numbers.

## Render free plan

Set the Render **Build Command** to:

```bash
bash build.sh
```

Set the **Start Command** to:

```bash
gunicorn migrantcenter.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 90
```

`build.sh` installs dependencies, collects static assets, applies committed migrations, creates permission groups, and safely ensures the environment-configured administrator exists. It intentionally does **not** import member files.

Required production variables include:

```env
SECRET_KEY=...
DEBUG=False
USE_SQLITE=False
DATABASE_URL=...
ALLOWED_HOSTS=mrnilam.org.np,www.mrnilam.org.np,.onrender.com
CSRF_TRUSTED_ORIGINS=https://mrnilam.org.np,https://www.mrnilam.org.np
CLOUDINARY_URL=...
ADMIN_USERNAME=...
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
RESET_ADMIN_PASSWORD=False
```

Optional email variables:

```env
EMAIL_NOTIFICATIONS_ENABLED=True
RESEND_API_KEY=...
DEFAULT_FROM_EMAIL=MRN Ilam <notifications@mrnilam.org.np>
ADMIN_NOTIFICATION_EMAIL=...
```

## Production deployment sequence

1. Back up Neon/PostgreSQL.
2. Run all checks and tests locally.
3. Commit migrations; never run `makemigrations` in Render.
4. Push and let `bash build.sh` deploy.
5. Verify `/health/` and application logs.
6. Inspect normalized backfill counts in admin.
7. Run workbook imports through a separately reviewed one-time deployment mechanism or a trusted local machine connected to the production database. Never place an import in `build.sh`.
8. Reconcile reports and confirm deleted records remain zero.

## Free-Render one-time command policy

Because free Render lacks an interactive shell, do not create public maintenance URLs. For a truly necessary one-time command, add a narrowly scoped, idempotent, environment-flagged line to `build.sh`, deploy once, verify logs, remove the flag and command, and deploy again. Membership imports are intentionally excluded because they require human report review.

## Documentation

- `docs/AUDIT.md`
- `docs/MEMBERSHIP_MIGRATION_AND_IMPORT.md`
- `docs/PRODUCTION_CHECKLISTS.md`
- `audit_reports/workbook-audit.json`
- `audit_reports/source-membership-rows.csv`
- `audit_reports/multiple-membership-candidates.csv`
- `audit_reports/potential-duplicate-review.csv`
- `audit_reports/non-data-rows.csv`
