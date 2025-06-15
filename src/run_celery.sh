#!/usr/bin/env bash

set -e

echo "Starting Celery inside xvfb..."

xvfb-run --auto-servernum --server-args="-screen 0 1920x1080x24" \
    celery -A apps.celery.celery_app worker --pool=threads --loglevel=info -c 1
