#!/bin/bash
set -e

echo "🚀 Running Alembic migrations..."
alembic upgrade head

echo "✅ Starting FastAPI with Gunicorn + Uvicorn workers..."
exec gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --workers 4 --timeout 60
