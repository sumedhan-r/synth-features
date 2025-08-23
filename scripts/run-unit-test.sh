#!/bin/bash
docker compose -f docker/docker-compose.test.yml stop
docker compose -f docker/docker-compose.test.yml rm -f

docker compose -f docker/docker-compose.test.yml build unit-test
docker compose -f docker/docker-compose.test.yml up unit-test