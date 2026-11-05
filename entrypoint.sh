#!/bin/sh
set -e
mkdir -p /data 2>/dev/null || true
echo "Starting Expense Tracker on port 3000..."
exec gunicorn \
  --bind 0.0.0.0:3000 \
  --workers 2 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  app:app
