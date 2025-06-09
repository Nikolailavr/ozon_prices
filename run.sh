#!/bin/bash

docker volume prune -f
#docker compose --env-file ./src/.env up -d redis celery-1 pg flower
#docker compose --env-file ./src/.env up --build app
docker compose --env-file ./src/.env up --build
docker image prune -f