#!/bin/bash
docker compose -f docker/docker-compose.yml stop
docker compose -f docker/docker-compose.yml rm -f

rm -rf db/redis/redis-volume

docker compose -f docker/docker-compose.yml --env-file db.env build
docker compose -f docker/docker-compose.yml --env-file db.env up -d