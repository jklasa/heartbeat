#!/bin/bash

line="\n========================================================================"

echo -e $line
echo -e "Confluent Platform\n"
microk8s kubectl config set-context --current --namespace=heartbeat

microk8s kubectl apply -f k8s/namespace.yaml

microk8s kubectl apply -f k8s/confluent/platform.yaml


# Common
echo -e $line
echo -e "Common\n"

microk8s kubectl create configmap common-configs \
    --from-file=kafka.ini=src/common/config/kafka.ini \
    --from-file=registry.json=src/common/config/registry.json \
    --dry-run=client -o yaml | microk8s kubectl apply -f -

# Twitter ingest
echo -e $line
echo -e "Twitter Ingest\n"

microk8s kubectl create configmap ingest-configs \
    --from-file=ingest.yaml=src/ingest/config/ingest.yaml \
    --from-file=ingest.rules=src/ingest/config/ru-ukr.rules \
    --dry-run=client -o yaml | microk8s kubectl apply -f -

microk8s kubectl create secret generic twitter-oauth \
    --from-literal=bearer=$TWITTER_BEARER \
    --dry-run=client -o yaml | microk8s kubectl apply -f -

microk8s kubectl apply -f k8s/ingest.yaml

# Sentiment analysis
echo -e $line
echo -e "Sentiment Analysis\n"

microk8s kubectl create configmap analyze-configs \
    --from-file=analyzer.yaml=src/analyze/config/analyzer.yaml \
    --dry-run=client -o yaml | microk8s kubectl apply -f -

microk8s kubectl apply -f k8s/analyze.yaml

# Influx
echo -e $line
echo -e "Influx Sink\n"

microk8s kubectl create secret generic idb-auth \
    --from-literal=token=$IDB_TOKEN \
    --dry-run=client -o yaml | microk8s kubectl apply -f -

microk8s kubectl create configmap idb-configs \
    --from-file=idb.yaml=src/idb/config/idb.yaml \
    --dry-run=client -o yaml | microk8s kubectl apply -f -

microk8s kubectl apply -f k8s/idb.yaml
