#!/bin/bash

line="\n========================================================================"

echo -e $line
echo -e "Confluent Platform\n"
microk8s kubectl config set-context --current --namespace=heartbeat

microk8s kubectl apply -f k8s/namespace.yaml

microk8s kubectl apply -f k8s/confluent/platform.yaml


# Twitter ingest
echo -e $line
echo -e "Twitter Ingest\n"
microk8s kubectl create configmap ingest-configs \
    --from-file=ingest.ini=ingest/ingest.ini \
    --from-file=ingest.rules=ingest/test.rules \
    --dry-run=client -o yaml | microk8s kubectl apply -f -

microk8s kubectl create secret generic twitter-oauth \
    --from-literal=bearer=$TWITTER_BEARER \
    --dry-run=client -o yaml | microk8s kubectl apply -f -

microk8s kubectl apply -f k8s/ingest.yaml
