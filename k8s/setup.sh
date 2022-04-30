#!/bin/bash

# Requirements:
#   * Installed:
#       - microk8s with helm, dns, storage
#       - kubectl

# 1 namespace
# 2 components
function install() {
    components=$1
    for comp in "${components[@]}"; do
        helm upgrade --install \
            $comp \
            ./confluent-operator \
            --values $3 \
            --namespace $2 \
            --set $comp.enabled=true
    done
}

#============================================================
NS="heartbeat"

microk8s kubectl apply -f namespace.yaml
microk8s kubectl config set-context --current --namespace=$NS

VALUES_FILE="helm/providers/private.yaml"

#components=(operator zookeeper kafka schemaregistry connectors)

#install $components $NS $VALUES_FIlE
helm upgrade --install confluent-operator \
    . \
    --values $VALUES_FILE \
    --namespace $NS
