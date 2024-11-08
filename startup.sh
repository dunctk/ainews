#!/bin/sh
set -e
python manage.py migrate
python manage.py collectstatic --no-input

granian --interface asgi --host 0.0.0.0 --port 80 --workers 4 curator.asgi:application
