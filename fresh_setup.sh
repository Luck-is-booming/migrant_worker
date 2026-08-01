#!/usr/bin/env bash
set -euo pipefail

python manage.py check
python manage.py migrate --noinput
python manage.py setup_staff_groups
python manage.py ensure_admin
python manage.py collectstatic --noinput

echo "Fresh application setup completed."
echo "Run the documented member imports after reviewing dry-run reports."
