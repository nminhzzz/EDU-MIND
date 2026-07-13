#!/bin/sh
# entrypoint.sh — Production startup script
#
# 1. Run Alembic migrations (idempotent — safe to run on every deploy)
# 2. Start the application server

set -e

echo "==> Initializing database..."
python pre_start.py

echo "==> Starting Gunicorn..."
exec gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
