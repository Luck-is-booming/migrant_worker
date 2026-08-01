# MRN Ilam — Clean Master Rebuild

This package is designed to replace the damaged local repository. It contains no database, no media, no secrets, and no Git history.

## Local setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# set USE_SQLITE=True and DEBUG=True locally
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Fresh member import

Run dry-runs first, inspect CSV reports, then run the same commands without `--dry-run`.

```bash
python manage.py import_members "data/membership_sources/Life Time Member of MRN District.xlsm" --level district --unit-name "Ilam District" --dry-run --report import_reports/district.csv
python manage.py import_members "data/membership_sources/MRN Ilam nagar level all Member List.xlsm" --level municipality --unit-name "Ilam Municipality" --dry-run --report import_reports/municipality.csv
python manage.py import_phakphokthum_committee --dry-run --report import_reports/phakphokthum.csv
```

Public member results are ordered by organization unit, membership category, and numeric membership number.
