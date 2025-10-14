#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn MainProject.wsgi:application -b 0.0.0.0:8000