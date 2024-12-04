#!/bin/sh
set -e
uv run manage.py migrate
uv run manage.py collectstatic --no-input

uv run manage.py scrape      

uv run manage.py 
uv run granian --interface asgi --host 0.0.0.0 --port 80 --workers 4 curator.asgi:application
