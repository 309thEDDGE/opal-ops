#! /bin/bash

cd $(dirname $0)
DOCKER_LOGINS="$HOME/.docker/config.json"

# refresh docker login credentials
docker login registry.il2.dso.mil
docker login registry1.dso.mil

# start minikube
minikube status || minikube start

# set up a few things
tar -C ../docker-compose/jupyterhub/ -cf base/extra_resources/jupyterhub-conf-dir.tar config
cp $DOCKER_LOGINS base/extra_resources/dockerconfig.json

# make it go
kubectl apply -k overlays/local_dev

# post-startup stuff
kubectl config set-context --current --namespace=opal

echo "Waiting for traefik to be ready..."
kubectl wait deployment/traefik --for condition=available --timeout=300s

echo "Waiting for keycloak to be ready..."
kubectl wait deployment/keycloak --for condition=available --timeout=300s
# restart minio (has to start after keycloak)
MINIO_POD=$(kubectl get pods -o json | jq -r '.items[] | select(.metadata.name | test("minio-")).metadata.name')
kubectl delete pod $MINIO_POD

echo "-------------------------------------------------------------"
echo "Run 'minikube tunnel' in a seperate terminal"
echo "Then opal will be available at opal-k8.10.96.30.9.nip.io"
echo "-------------------------------------------------------------"