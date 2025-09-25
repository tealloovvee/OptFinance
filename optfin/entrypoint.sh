set -e

python manage.py migrate --noinput

python manage.py collectstatic --noinput

exec gunicorn optfin.wsgi:application -b 0.0.0.0:8000