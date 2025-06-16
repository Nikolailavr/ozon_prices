#!/bin/bash

docker volume prune -f
#docker compose --env-file ./src/.env up -d --build
docker compose --env-file ./src/.env up -d --build pg celery_tg app flower redis
docker image prune -f