#!/bin/bash

docker volume prune -f
#docker compose --env-file ./src/.env up --build
docker compose --env-file ./src/.env up -d --build redis pg flower
docker compose --env-file ./src/.env up -d --build app
#docker compose --env-file ./src/.env up -d --build vnc
#docker logs ozon_prices-celery-1-1 -f
#docker compose up -d --build
docker image prune -f

#cd src
#poetry run celery -A apps.celery.celery_app worker --pool=threads --loglevel=info -c 1