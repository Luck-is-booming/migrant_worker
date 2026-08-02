# Deployment, backup and rollback

## Before deployment

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

Back up Neon/PostgreSQL before applying new migrations. Confirm that `.env`, database files, private exports, media, payment evidence and counseling attachments are not committed.

## Render

- Build: `bash build.sh`
- Start: `gunicorn migrantcenter.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 90`
- Health check: `/health/`

The build installs dependencies, checks Django, collects static files, migrates, creates permission groups and safely ensures the environment-configured administrator. It does not import or overwrite operational data.

## Cloudinary/private-file verification

After deployment, use a controlled counseling request and payment application to verify:

1. Public content images upload and render.
2. New counseling/payment files are uploaded as authenticated Cloudinary assets.
3. Anonymous direct access is denied.
4. Authorized staff can open the protected admin download/view.
5. Replaced/deleted test files can be cleaned up.

The application generates short-lived signed URLs only after Django permission checks. Existing legacy public object names remain readable to authorized staff for migration; the launch-readiness audit reports them. Do not put private asset URLs in templates, logs, email or analytics.

## Production member import from a trusted machine

Temporarily export the production `DATABASE_URL`, set `USE_SQLITE=False`, verify the database host, run dry-runs, then real imports. Unset the variables immediately afterward. Never expose imports as public URLs and never put recurring imports in `build.sh`.

## Rollback

1. Stop further admin changes if data integrity is in question.
2. Preserve logs and the failing release identifier.
3. Roll Render back to the last known-good Git commit/deploy.
4. If a schema/data migration changed production data, restore the pre-deployment database backup or apply the documented reverse migration only after testing it against a copy.
5. Verify `/health/`, admin login, member counts, public pages and forms.

Code rollback does not automatically reverse a database migration. Treat code and database rollback as separate controlled actions.
