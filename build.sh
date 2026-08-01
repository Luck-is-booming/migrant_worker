#!/usr/bin/env bash
set -o errexit
set -o pipefail

echo "Installing dependencies"
pip install -r requirements.txt

echo "Collecting static files"
python manage.py collectstatic --noinput

echo "Applying committed migrations"
python manage.py migrate --noinput

echo "Creating staff permission groups"
python manage.py setup_staff_groups

echo "Ensuring environment-configured administrator exists"
python manage.py ensure_admin

echo "Build complete"
