#!/bin/sh
set -e
mkdir -p /data || true
exec gunicorn --bind 0.0.0.0:3000 --workers 2 --timeout 60 app:app
