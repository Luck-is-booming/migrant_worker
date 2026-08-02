#!/usr/bin/env bash
set -euo pipefail

python manage.py check
python manage.py migrate --noinput
python manage.py setup_staff_groups
python manage.py collectstatic --noinput

printf '%s\n' "Fresh application setup completed."
printf '%s\n' "Create a superuser with: python manage.py createsuperuser"
printf '%s\n' "Optionally seed verified official links/FAQs: python manage.py seed_launch_content"
printf '%s\n' "Dry-run and review member imports before committing them."
