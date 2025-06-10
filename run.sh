#!/bin/bash

docker volume prune -f
docker compose --env-file ./src/.env up -d --build redis pg flower
#docker compose --env-file ./src/.env up -d --build app
#docker compose --env-file ./src/.env up --build
docker image prune -f
cd src
poetry run celery -A apps.celery.celery_app worker --pool=threads --loglevel=info -c 1