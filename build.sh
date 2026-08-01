#!/usr/bin/env bash
<<<<<<< HEAD

set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Applying database migrations..."
python manage.py migrate --no-input

echo "Ensuring administrator exists..."
python manage.py ensure_admin

if [[ "${IMPORT_PHAKPHOKTHUM:-False}" == "True" ]]; then
    echo "Importing Phakphokthum committee..."
    python manage.py import_phakphokthum_committee
fi

echo "Build completed successfully."
=======
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
>>>>>>> 1d670fd (refactor)
