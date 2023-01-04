#! /bin/bash

cd $(dirname $0)

# start minikube
minikube status || minikube start --network-plugin=cni

if ! something 2&> /dev/null; then
    echo "[ERROR] Cilium CNI driver not installed. Instructions at https://kubernetes.io/docs/tasks/administer-cluster/network-policy-provider/cilium-network-policy/"
    exit
fi

cilium install

bash ./start_local_kustomize.bash