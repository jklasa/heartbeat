#!/bin/bash

# Requirements:
#   * Installed:
#       - microk8s with helm, dns, storage
#       - kubectl

#============================================================
NS="heartbeat"

microk8s kubectl apply -f k8s/namespace.yaml
microk8s kubectl config set-context --current --namespace=$NS

helm upgrade --install confluent-operator confluent/confluent-for-kubernetes --namespace $NS --values k8s/confluent/private.yaml

kubectl apply -f k8s/confluent/platform.yaml

helm install influxdb influxdata/influxdb2 --version 2.0.12

echo $(kubectl get secret influxdb-influxdb2-auth -o "jsonpath={.data['admin-password']}" --namespace heartbeat | base64 --decode) > k8s/influx.pw

./scripts/k8s-update.sh
