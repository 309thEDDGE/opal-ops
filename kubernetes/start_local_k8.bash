#!/bin/bash

##### setup #####
cd $(dirname $0)

DOCKER_LOGINS="$HOME/.docker/config.json"

docker login registry.il2.dso.mil
docker login registry1.dso.mil

minikube status || minikube start
# minikube addons enable ingress

kubectl config set-context --current --namespace=jupyterhub
kubectl create namespace jupyterhub

##### args #####
ARGS=$(getopt -o '' -n start_k8 --long soft-reset,reset -- "$@")

eval set -- "$ARGS"
while true; do
    case $1 in
        --soft-reset )
            # delete old deployments so new ones can be created
            # with updated configmappings/secrets
            kubectl delete deployment --all
            shift 1
            ;;
        --reset )
            # delete old deployments and volumes
            kubectl delete deployment --all
            kubectl delete pod --all
            kubectl delete pvc --all
            shift 1
            ;;
        -- )
            break
            ;;
    esac
done

##### secrets #####
kubectl delete secret regcred
kubectl create secret generic regcred \
--from-file=.dockerconfigjson=$DOCKER_LOGINS \
--type=kubernetes.io/dockerconfigjson \
-n jupyterhub

kubectl delete secret tls-certs
kubectl create secret tls tls-certs \
--cert=extra_resources/local/tls.crt \
--key=extra_resources/local/tls.key \
-n jupyterhub

kubectl delete secret minio-certs
kubectl create secret generic minio-certs \
--from-file=extra_resources/local/tls.crt \
-n jupyterhub

kubectl delete secret token-env
kubectl create secret generic token-env \
--from-env-file=../docker-compose/.env.secrets

##### config #####
# -C changes the working directory of tar
tar -C ../docker-compose/jupyterhub/ -cvf jupyterhub-conf-dir.tar config
kubectl delete configmap jupyterhub-config
kubectl create configmap jupyterhub-config \
--from-file=jupyterhub-conf-dir.tar

kubectl delete configmap jupyterhub-config-py
kubectl create configmap jupyterhub-config-py \
--from-file=extra_resources/jupyterhub_config.py

kubectl delete configmap jupyterhub-startup-script
kubectl create configmap jupyterhub-startup-script \
--from-file=extra_resources/startup_script.bash

kubectl delete configmap singleuser-torch-dockerfile
kubectl create configmap singleuser-torch-dockerfile \
--from-file=../docker-compose/singleuser/Dockerfile

kubectl delete configmap keycloak-setup-script
kubectl create configmap keycloak-setup-script \
--from-file=../docker-compose/keycloak/keycloak_script.sh

kubectl delete configmap deployment-env
kubectl create configmap deployment-env \
--from-env-file=extra_resources/local/k8.env

kubectl delete configmap opal-env
kubectl create configmap opal-env \
--from-env-file=../docker-compose/.env

##### deployments/services #####
kubectl delete job keycloak-setup

# note to self: minio needs to be started *after* keycloak
kubectl apply \
-f init_singleuser_image.yaml \
-f jupyterhub.yaml \
-f postgres.yaml \
-f traefik.yaml \
-f catalog.yaml \
-f keycloak.yaml \
-f extra_resources/local/ingress.yaml \

echo "waiting for keycloak to be ready..."
kubectl wait deployment/keycloak --for condition=available --timeout=300s

kubectl apply \
-f minio.yaml 

##### other setup for local deployment #####

# wait for traefik to be ready
echo "waiting for traefik to be ready..."
kubectl wait deployment/traefik --for condition=available --timeout=300s

echo "-------------------------------------------------------------"
echo "Run 'minikube tunnel' in a seperate terminal"
echo "Then opal will be available at opal-k8.10.96.30.9.nip.io"
echo "-------------------------------------------------------------"