#! /bin/bash

cd $(dirname $0)
DOCKER_LOGINS="$HOME/.docker/config.json"

# refresh docker login credentials
docker login registry1.dso.mil

# start minikube
minikube status || minikube start

# set up a few things
tar -C ../docker-compose/jupyterhub/ -cf base/extra_resources/jupyterhub-conf-dir.tar config
#pushd ../docker-compose/
#if [[ ! -d opal ]]
#then
#    printf "../docker-compose/opal/ not found. Please clone it and rerun this script"
#    exit
#fi
#if [[ ! -d weave ]]
#then
#    git clone https://github.com/309thEDDGE/weave.git
#else
#    pushd weave
#    git pull
#    popd
#fi
#popd
#tar -C ../docker-compose/ -cf base/extra_resources/opal.tar opal
#tar -C ../docker-compose/ -cf base/extra_resources/weave.tar weave
cp $DOCKER_LOGINS base/extra_resources/dockerconfig.json
python3 ../docker-compose/configuration/generate_secrets.py overlays/local_dev_prod/k8s-context.json > base/extra_resources/.env.secrets
if [[ ! -f overlays/local_dev_prod/tls.crt ]] || [[ ! -f overlays/local_dev_prod/tls.key ]]
   then openssl req -new -newkey rsa:2048 -days 365 -nodes -x509  -subj /CN=*.10.96.30.9.nip.io -extensions san -config overlays/local_dev_prod/ssl.conf -keyout overlays/local_dev_prod/tls.key -out overlays/local_dev_prod/tls.crt
fi

# make it go
kubectl apply -k overlays/local_dev_prod

# post-startup stuff
kubectl config set-context --current --namespace=opal

echo "Waiting for traefik to be ready..."
kubectl wait deployment/traefik --for condition=available --timeout=500s

echo "Waiting for keycloak to be ready..."
kubectl wait deployment/keycloak --for condition=available --timeout=500s
# restart minio (has to start after keycloak)
MINIO_POD=$(kubectl get pods -o json | jq -r '.items[] | select(.metadata.name | test("minio-")).metadata.name')
kubectl delete pod $MINIO_POD

echo "-------------------------------------------------------------"
echo "Run 'minikube tunnel' in a seperate terminal"
echo "Then opal will be available at opal-k8.10.96.30.9.nip.io"
echo "-------------------------------------------------------------"
