#!/bin/sh
set -e

cd templates
if [ ! -d "dist" ] || [ ! -f "dist/index.html" ]; then
    echo "Building frontend..."
    npm install
    npm run build
fi
cd ..

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn MainProject.wsgi:application -b 0.0.0.0:8000