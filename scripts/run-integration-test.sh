#!/bin/bash
docker compose -f docker/docker-compose.test.yml stop
docker compose -f docker/docker-compose.test.yml rm -f

docker compose -f docker/docker-compose.test.yml --env-file db.env up -d redis

docker compose -f docker/docker-compose.test.yml build
docker compose -f docker/docker-compose.test.yml up integration-test
