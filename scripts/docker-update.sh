#!/bin/bash

declare -a services=(ingest analyze)

for service in "${services[@]}"; do
    docker build ./src/ -t jklasa27/heartbeat:$service -f ./src/${service}/Dockerfile
    docker push jklasa27/heartbeat:$service
done
