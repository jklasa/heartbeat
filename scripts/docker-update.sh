#!/bin/bash

declare -a services=(ingest)

for service in "${services[@]}"; do
    docker build ./$service -t jklasa27/heartbeat:$service
    docker push jklasa27/heartbeat:$service
done
