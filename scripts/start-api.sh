#!/usr/bin/env bash

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding default users..."
python scripts/seed_users.py

echo "Starting application..."
exec gunicorn -k uvicorn.workers.UvicornWorker -c ./src/app/gunicorn_conf.py src.main:app