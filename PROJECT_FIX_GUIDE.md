# MRN Ilam Project Fix Guide

This version focuses on safety, reliable membership approval, email notifications,
and importing the Phakphokthum rural committee list.

## 1. What changed

- Removed the public `setup-admin-user/` backdoor and hardcoded `admin/admin` credentials.
- Replaced guessable payment IDs with signed, tamper-resistant URLs.
- Prevented a second active payment proof from being submitted for the same application.
- Read membership fees from `MANUAL_PAYMENT_CONFIG` instead of hardcoding them in the view.
- Fixed payment approval so it no longer writes the removed `ward_no` field into `Member`.
- Linked each online application to exactly one final `Member` record.
- Assigned online members to the correct municipality/rural-municipality registry.
- Restored normal numeric membership numbering inside each registry and membership type.
- Added rejected payment state and safer admin actions.
- Added optional applicant email and automatic notifications.
- Added screenshot type and 5 MB size validation.
- Made the homepage member count live instead of hardcoded.
- Made registry filter options load dynamically from the database.
- Marked private payment/status pages `noindex`.
- Added a DOCX importer for the 11-person Phakphokthum committee.
- Expanded `.gitignore` and added a safe `.env.example`.
- Added tests for the critical approval and import flows.

## 2. Before deploying

Rotate any credentials that were ever stored in or shared through `.env`:

- Django `SECRET_KEY`
- PostgreSQL `DATABASE_URL`
- Cloudinary credentials
- Resend API key

Do not commit `.env`, `db.sqlite3`, payment screenshots, or uploaded media.

## 3. Install and migrate

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py check --deploy
python manage.py test
```

Create an administrator safely with Django's built-in command:

```bash
python manage.py createsuperuser
```

There is intentionally no public web URL for creating an administrator anymore.

## 4. Render environment variables

Copy the names from `.env.example` into Render's Environment page. At minimum:

```text
SECRET_KEY=<new-long-random-value>
DEBUG=False
ALLOWED_HOSTS=mrnilam.org.np,www.mrnilam.org.np,<service>.onrender.com
CSRF_TRUSTED_ORIGINS=https://mrnilam.org.np,https://www.mrnilam.org.np
DATABASE_URL=<render-postgres-url>
CLOUDINARY_URL=<cloudinary-url>
GENERAL_MEMBER_AMOUNT=500
LIFE_MEMBER_AMOUNT=5000
```

## 5. Email setup

The project uses Django Anymail with Resend.

Add these Render variables:

```text
RESEND_API_KEY=re_...
DEFAULT_FROM_EMAIL=MRN Ilam <notifications@mrnilam.org.np>
ADMIN_NOTIFICATION_EMAIL=info@mrnilam.org.np
EMAIL_NOTIFICATIONS_ENABLED=True
SITE_URL=https://mrnilam.org.np
```

The sender address must belong to a domain verified in Resend. During local development,
if `RESEND_API_KEY` is absent, Django prints emails to the terminal instead of crashing.

Test production email after deployment:

```bash
python manage.py send_test_email --to your-email@example.com
```

Emails now fire when:

- A contact message is submitted: staff receives it and can reply directly.
- A membership application is submitted: staff is notified; applicant is notified if email was supplied.
- A payment proof is uploaded: staff and optional applicant receive confirmation.
- A payment is approved/rejected: optional applicant receives the decision.

## 6. Import the Phakphokthum committee

The source is:

```text
data/Phakphokthum Rural Commeetee.docx
```

Run:

```bash
python manage.py import_phakphokthum_committee
```

The source document provides 11 names, positions, addresses, and most phone numbers,
but it does **not** provide membership type or membership number. Therefore:

- New records default to `general` membership.
- New numeric member numbers are generated inside the
  `Phakphokthum Rural Municipality` registry.
- Phone numbers are stored but hidden publicly by default.
- Existing matching names are updated without overwriting their existing membership type.

Use a different type only if the organization confirms it:

```bash
python manage.py import_phakphokthum_committee --membership-type life
```

To deliberately replace every existing row in that exact registry:

```bash
python manage.py import_phakphokthum_committee --replace-unit
```

Do not use `--replace-unit` unless you intend to delete that registry's current records first.

To show imported phone numbers publicly:

```bash
python manage.py import_phakphokthum_committee --show-phone
```

Privacy-safe default is to keep phone numbers hidden.

## 7. Approval flow after the fix

1. Visitor submits membership form.
2. A `core.Membership` application is created.
3. Django creates a signed payment link; raw numeric IDs are not exposed.
4. Visitor uploads one payment proof.
5. Admin reviews the proof in Django admin.
6. Approval updates the application to completed.
7. Approval creates or updates one linked `members.Member`.
8. The member receives the next numeric number inside their registry and type.
9. The member appears publicly; their phone remains hidden unless an admin enables it.

## 8. Important admin rule

Approve and reject payments from **Payments → Manual payments**.
Do not manually toggle application approval fields. Those fields are read-only now so the
payment decision and public member record cannot drift apart.
