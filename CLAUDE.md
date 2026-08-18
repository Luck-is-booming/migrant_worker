# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MRN Ilam is a Django platform for foreign-employment awareness, private counseling, verified resources, organizational publishing, and membership management with optional manual membership-payment verification. The public wording deliberately presents the organization as an information/awareness/counseling/referral service — it does **not** claim to issue visas, recruit workers, or guarantee jobs/migration outcomes. Keep that framing in mind when touching public-facing copy.

Stack: Python 3.13, Django 6.0, PostgreSQL in production (SQLite for local dev/tests), Django templates + first-party CSS/JS, Cloudinary-compatible media storage, Resend via django-anymail, Gunicorn + WhiteNoise, deployed on Render.

## Development Safety Rules

- Never expose, print, commit, or modify secrets or credentials.
- Never modify production environment variables.
- Never make destructive database changes without explicitly explaining the migration and getting my approval.
- Never change membership numbering behavior without first explaining the impact.
- Never bypass existing authentication or permission checks.
- Never expose private payment evidence or sensitive member information.
- Preserve existing bilingual Nepali/English behavior.
- Before making large architectural changes, explain the proposed approach first.
- Prefer small, targeted changes over unnecessary rewrites.
- Before modifying code, inspect the existing implementation and related tests.

## Common commands

Setup:
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DEBUG=True, USE_SQLITE=True locally
python manage.py migrate
python manage.py setup_staff_groups
python manage.py createsuperuser
python manage.py seed_launch_content
python manage.py runserver
```

Testing:
```bash
python manage.py test                          # full suite (in-memory SQLite)
python manage.py test members.tests.MembershipNumberingTests -v 2   # single test case
python manage.py check
python manage.py makemigrations --check --dry-run
```

To verify simultaneous membership-number allocation under real PostgreSQL locking (not covered by the default SQLite suite), point at a disposable database — never at production:
```bash
TEST_DATABASE_URL='postgresql://...' python manage.py test members.tests.PostgreSQLMembershipNumberConcurrencyTests -v 2
```

Lint/format (config in `pyproject.toml`): `ruff check .` and `black .`.

Translations:
```bash
python manage.py makemessages -l ne
# hand-review locale/ne/LC_MESSAGES/django.po — never publish machine-translated Nepali unreviewed
python manage.py compilemessages
```

Launch/data ops:
```bash
python manage.py audit_launch_readiness          # missing contacts/payment setup/resources without changing data
python manage.py import_members "<xlsm>" --level district --unit-name "..." --dry-run --report import_reports/x.csv
python manage.py export_member_registry exports/members.csv
```
Always dry-run imports first and read `docs/MEMBER_IMPORT.md`; re-running an unchanged source is idempotent and never deletes rows merely absent from a later file. Treat private exports (`--include-private-contact`) as confidential, kept outside Git.

## Architecture

Five Django apps with a deliberate split:
- **core** — org info, services, verified resources, FAQ, leadership, contact, membership applications, payment configuration, privacy/disclaimer/program pages.
- **counseling** — private requests, categories, notes, contact attempts, assignment, status/retention workflow.
- **members** — people, official memberships, org units, categories, permanent number ledger, imports, duplicate review, public directory.
- **payments** — private payment evidence, status tracking, review audit, approval service.
- **blog** — bilingual news, notices, alerts, events/programs, counseling updates, localized SEO metadata.

**Person vs. MembershipRecord**: `Person` (members/models.py) holds one individual and private contact info; `MembershipRecord` holds each separate membership relationship (FK to `Person`, `MembershipCategory`, `OrganizationUnit`). One person can hold both General and Life Membership, or memberships in different org units, without duplicating identity data. `core.Membership` is a different thing — the public *application* row (unapproved, payment-pending); it only becomes a real `Person`/`MembershipRecord` after payment approval (`payments.ManualPayment.approve()`). `members.Member` is an explicitly legacy table kept only for historical/audit compatibility (`legacy_member` FK) — don't build new features on it.

**Membership numbering** (`members/numbering.py`, `docs/MEMBERSHIP_NUMBERING.md`): numbers are unique per (`MembershipCategory`, `OrganizationUnit`) scope, not globally — the same numeric value can legitimately exist in different district/municipality or category registries. `MembershipNumberSequence` holds the next number per scope and is locked with PostgreSQL `SELECT ... FOR UPDATE` during allocation; a DB uniqueness constraint is the first guard. `MembershipNumberIssue` is a permanent ledger of every number ever issued (second guard, scoped-unique) — numbers are never recycled, even after archive or permanent deletion. Editing name/phone/status/address/designation never changes a number; `MembershipRecord.clean()` actively blocks replacing an issued number through ordinary edits — archive the record instead. Archive/restore keep the same number; payment approval allocates through this same allocator.

**Authentication & permissions**: standard `django.contrib.auth` session auth — no public user accounts, only Django Admin staff. `python manage.py setup_staff_groups` (`core/management/commands/setup_staff_groups.py`) creates least-privilege groups with a hard-coded permission list per group: `Membership Manager`, `Counseling Staff`, `Content Editor`, `Payment Reviewer`, plus `Administrator` (all permissions). `python manage.py ensure_admin` bootstraps/maintains one superuser purely from `ADMIN_USERNAME`/`ADMIN_EMAIL`/`ADMIN_PASSWORD` env vars, idempotently, and only resets the password when `RESET_ADMIN_PASSWORD=True` is explicitly set — both commands run automatically in `build.sh`. `migrantcenter/admin_helpers.py` provides `SuperuserOnlyAdminMixin`/`SuperuserReadOnlyAdminMixin` to hide sensitive internal models (numbering sequences, audit ledgers) from ordinary staff. `migrantcenter/admin_site.py` (`MRNAdminSite`) is a custom admin site that relabels/reorders apps and injects permission-gated dashboard counts — extend it rather than the default `admin.site` when adding admin-wide behavior. `migrantcenter/middleware.py` adds `AdminLoginRateLimitMiddleware` (10 failed `/admin/login` POSTs per 15 min per hashed IP, cache-backed) and `SecurityHeadersMiddleware` (strict CSP, looser only on `/admin/*` for Django's inline admin JS/CSS).

**Public/private boundary**: public member pages expose only approved public fields. Phone, email, payment screenshots, counseling details, source-IP hashes, internal notes, and duplicate-review evidence are staff-only. New counseling/payment files use `core.storage.AuthenticatedCloudinaryStorage` (Cloudinary's authenticated delivery type) with the DB storing only opaque resource metadata, never a reusable URL; staff access goes through permission-checked Django admin views (e.g. `ManualPaymentAdmin.evidence_view`) that mint five-minute signed URLs on demand. Local dev/tests use plain local/in-memory storage instead. Older deployments may still have legacy public Cloudinary object names — `audit_launch_readiness` reports how many need migration.

**Payment workflow** (`payments/models.py`, `payments/views.py`, `payments/tokens.py`): fully manual, QR-based — no payment gateway. An admin must first fill in and activate the singleton `MembershipPaymentSettings` row (verified fees, recipient name, QR image, bilingual instructions); `is_ready` requires every field verified, and public applications stay paused until then — a deliberate guard against an unverified/guessed fee or QR going live. Applicants reach the upload form/status page only through signed, expiring tokens (`django.core.signing`; 30-day membership link, 90-day payment-status link) — no login required, but links can't be guessed. `ManualPayment.status` is one of `pending` → `needs_review` / `approved` / `rejected`; a DB constraint allows only one open-or-approved payment per application, and transaction references must be unique when non-blank. Submission and every review transition (`approve()`, `mark_needs_review()`, `reject()`) run inside `transaction.atomic()` with `select_for_update()`, and are idempotent — re-approving an already-approved payment is a no-op. `approve()` creates-or-links one `Person`, creates one `MembershipRecord`, and allocates a permanent number through the numbering allocator, all transactionally. `reject()` requires a non-empty applicant-facing `rejection_reason` (raises `ValidationError` otherwise) and is logged, along with every other transition, to `PaymentReviewEvent` for audit. External email failures must never roll back an otherwise-successful form submission (see `core/notifications.py`, `payments` notify calls).

**i18n**: `LANGUAGE_CODE = "ne"`, with `en`/`ne` routed via `django.conf.urls.i18n.i18n_patterns` in `migrantcenter/urls.py` — every public route is prefixed `/en/...` or `/ne/...` with canonical/alternate-language SEO metadata. Most public-facing models store `_ne`/`_en` field pairs and expose a `localized()`-computed property (`core/i18n_utils.py`) that picks the field for the active language rather than using Django's translation catalog for content — the `.po`/`.mo` catalog (`locale/ne/`) is only for UI strings wrapped in `gettext`/`{% trans %}`. Never guess/machine-translate a missing `_ne`/`_en` field — leave it blank rather than inventing organizational claims.

**Settings** (`migrantcenter/settings.py`): `USE_SQLITE` and `DEBUG` env flags select the database backend; `IS_PRODUCTION` is only true when not debug, `DATABASE_URL` is set, not using SQLite, and not under test — several security/production-only defaults (SSL redirect, secure cookies, HSTS) key off this flag, not off `DEBUG` alone.

## Deployment (Render)

Defined in `render.yaml`: one free-tier Python web service, build command `bash build.sh`, start command `gunicorn migrantcenter.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 90`, health check at `/health/`, `autoDeploy: true`. `build.sh` runs, in order: install deps → `manage.py check` → `makemigrations --check --dry-run` (fails the build if a model change lacks a committed migration) → `collectstatic` → `migrate` → `setup_staff_groups` → `ensure_admin`. It deliberately never imports members, seeds articles, overwrites content, or resets the admin password unless `RESET_ADMIN_PASSWORD=True` is explicitly set — don't add build-time steps that would do so silently. Secrets (`SECRET_KEY`, `DATABASE_URL`, `CLOUDINARY_URL`, `RESEND_API_KEY`, `DEFAULT_FROM_EMAIL`, `ADMIN_NOTIFICATION_EMAIL`, `ADMIN_USERNAME`/`ADMIN_EMAIL`/`ADMIN_PASSWORD`) are marked `sync: false` in `render.yaml` and set manually in the Render dashboard, not committed.

## Safety rules

- Never commit or paste real values for `SECRET_KEY`, `DATABASE_URL`, `CLOUDINARY_URL`, `RESEND_API_KEY`, or `ADMIN_PASSWORD` — `.env` is gitignored; only `.env.example` (blank placeholders) belongs in the repo.
- Never manually edit or delete a `MembershipNumberIssue` row or hand-assign a `membership_number` that bypasses `MembershipRecord.save()`'s allocator — numbers must never be recycled or duplicated within a scope.
- Never treat payment screenshots, counseling attachments/notes, phone/email, or source-IP hashes as public data — they must stay behind the authenticated Cloudinary storage and permission-checked admin views, never the default/public storage.
- Never bypass `build.sh`'s safeguards (no ad-hoc member import, content seeding, or admin password reset during deploy) and never run destructive import/export commands without `--dry-run` first, per `docs/MEMBER_IMPORT.md`.
- Never publish machine-generated Nepali content or invent organizational claims (fees, guarantees, embassy contacts, etc.) — leave a `_ne`/`_en` field blank rather than guessing.
- Keep private exports (`export_member_registry --include-private-contact`) out of Git and treat them as confidential.
- Payment rejection must always carry a human-written `rejection_reason`; don't add a code path that rejects without one.

Further reading: `docs/ARCHITECTURE.md`, `docs/MEMBERSHIP_NUMBERING.md`, `docs/MEMBER_IMPORT.md`, `docs/CLIENT_ADMIN_GUIDE.md`, `docs/DEPLOYMENT_AND_ROLLBACK.md`.

## Sibling directories (not this repo)

`/home/khesha/Desktop/project/` also contains several dated snapshot copies (`migrantcenter-before-*`) and delivery zip files alongside this repo. Those are point-in-time backups/deliverables, not branches of this codebase — don't edit them, and don't assume they're in sync with `migrantcenter/`.
