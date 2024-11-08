#!/bin/sh
set -e
uv run manage.py migrate
uv run manage.py collectstatic --no-input

granian --interface asgi --host 0.0.0.0 --port 80 --workers 4 curator.asgi:application
