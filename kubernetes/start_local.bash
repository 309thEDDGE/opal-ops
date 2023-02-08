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
cp ../docker-compose/.env.secrets base/extra_resources/.env.secrets

# generate certificates if necessary
if [ -f overlays/local_dev/tls.key ] && [ overlays/local_dev/tls.crt ]; then
    echo "Found local certificates"
else
    echo "Did not find local certificates"
    echo "Generating self-signed certificates..."
    openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
    -subj /CN=*.10.96.30.9.nip.io -extensions san -config cert_config.cfg \
    -keyout overlays/local_dev/tls.key -out overlays/local_dev/tls.crt
fi

# make it go
kubectl apply -k overlays/local_dev

# post-startup stuff
kubectl config set-context --current --namespace=opal

echo "Waiting for traefik to be ready..."
echo "You can check progress with `watch kubectl get pod`"
echo "A few errors/restarts are normal" # [1]
kubectl wait deployment/traefik --for condition=available --timeout=500s

echo "Waiting for keycloak to be ready..."
echo "You can check progress with `watch kubectl get pod`"
echo "A few errors/restarts are normal"
kubectl wait deployment/keycloak --for condition=available --timeout=500s
# restart minio (has to start after keycloak)
MINIO_POD=$(kubectl get pods -o json | jq -r '.items[] | select(.metadata.name | test("minio-")).metadata.name')
kubectl delete pod $MINIO_POD

echo "-------------------------------------------------------------"
echo "Run 'minikube tunnel' in a seperate terminal"
echo "Then opal will be available at opal-k8.10.96.30.9.nip.io"
echo "-------------------------------------------------------------"

# [1] Some services (i.e. opal-catalog-be) depend on postgres being up,
# but postgres often takes some time to start up. So when opal-catalog-be
# (for example) starts and postgres isn't ready, it crashes with an error.
# Fortunately this doesn't really matter, as part of what Kubernetes does is 
# restart pods that have crashed. Eventually postgres will be up, and 
# the Kubernetes cluster will restart the crashed opal-catalog-be pod, which
# will then start working.