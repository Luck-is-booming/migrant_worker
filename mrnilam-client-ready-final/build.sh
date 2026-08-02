#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' "Installing pinned dependencies"
pip install -r requirements.txt

printf '%s\n' "Running Django system checks"
python manage.py check

printf '%s\n' "Confirming model changes have committed migrations"
python manage.py makemigrations --check --dry-run

printf '%s\n' "Collecting static files"
python manage.py collectstatic --noinput

printf '%s\n' "Applying committed migrations"
python manage.py migrate --noinput

printf '%s\n' "Creating staff permission groups"
python manage.py setup_staff_groups

printf '%s\n' "Ensuring environment-configured administrator exists"
python manage.py ensure_admin

printf '%s\n' "Build complete; no member import or content overwrite was run."
