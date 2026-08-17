#!/bin/sh
# entrypoint.sh — Production startup script
#
# 1. Run Alembic migrations (idempotent — safe to run on every deploy)
# 2. Start the application server

set -e

echo "==> Starting Gunicorn..."
exec gunicorn app.main:app \
  --workers "${WEB_CONCURRENCY:-2}" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile -
