# Local setup and safe packaging

## Fresh local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py check
python manage.py migrate
python manage.py setup_staff_groups
python manage.py createsuperuser
python manage.py seed_launch_content
python manage.py test
python manage.py collectstatic --noinput
python manage.py runserver
```

## Safe ZIP for transfer

Run from the directory containing the project folder:

```bash
zip -r mrnilam-project.zip migrantcenter \
  -x 'migrantcenter/.git/*' \
     'migrantcenter/.env' \
     'migrantcenter/db.sqlite3' \
     'migrantcenter/*.sqlite3' \
     'migrantcenter/venv/*' \
     'migrantcenter/.venv/*' \
     'migrantcenter/media/*' \
     'migrantcenter/staticfiles/*' \
     'migrantcenter/backups/*' \
     'migrantcenter/import_reports/*' \
     'migrantcenter/**/__pycache__/*' \
     'migrantcenter/**/*.pyc'
```

Verify that secrets/private data are absent:

```bash
unzip -l mrnilam-project.zip | less
unzip -l mrnilam-project.zip | grep -E '(\.env$|db\.sqlite3|media/|backups/|import_reports/)'
```

The second command should return nothing sensitive.

Create a checksum:

```bash
sha256sum mrnilam-project.zip > mrnilam-project.zip.sha256
```

## Never send or commit

- `.env`
- database dumps without an approved secure transfer
- payment screenshots
- counseling attachments/submissions
- private exports/import reports
- administrator passwords
- Neon, Cloudinary or Resend secrets
