#!/usr/bin/env bash

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