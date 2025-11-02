#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

cron &

exec gunicorn MainProject.wsgi:application -b 0.0.0.0:8000