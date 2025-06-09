#!/bin/bash

docker volume prune -f
docker compose --env-file ./src/.env up --build
docker image prune -f