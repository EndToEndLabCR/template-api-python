#!/usr/bin/env bash

set -e

echo "Starting application..."
exec gunicorn -k uvicorn.workers.UvicornWorker -c ./src/app/gunicorn_conf.py src.main:app