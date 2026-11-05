#!/bin/sh
set -e
mkdir -p /data
python -c "from app import init_db; init_db()"
exec gunicorn --bind 0.0.0.0:3000 --workers 2 --timeout 60 app:app
