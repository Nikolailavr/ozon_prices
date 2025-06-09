#!/bin/bash

docker volume prune -f
docker compose --env-file ./src/.env up -d --build redis pg flower app
#docker compose --env-file ./src/.env up --build app
#docker compose --env-file ./src/.env up --build
docker image prune -f