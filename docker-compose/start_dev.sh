#!/bin/bash

cd `dirname $0`

FILE=./.env.secrets

if test -f "$FILE"; then
    echo "Found secrets file. Deploying"
else
    echo "Creating secrets file"
    cat << EOF > $FILE
COOKIE_SECRET=secret
JUPYTERHUB_API_TOKEN=`openssl rand -hex 32`
KEYCLOAK_JUPYTERHUB_CLIENT_SECRET=secret
KEYCLOAK_MINIO_CLIENT_SECRET=secret
JUPYTERHUB_CRYPT_KEY=`openssl rand -hex 32`
KEYCLOAK_SECRET=secret
MINIO_IDENTITY_OPENID_CLIENT_SECRET=secret
EOF
fi

if [[ $# > 0 ]]; then
    DEPLOYMENT=$1
else
    DEPLOYMENT="dev"
fi

if [[ -f "$DEPLOYMENT.docker-compose.yml" ]]; then
    COMPOSE_FILE="$DEPLOYMENT.docker-compose.yml"
elif [[ -f "$DEPLOYMENT.docker-compose.json" ]]; then
    echo "Could not find $DEPLOYMENT.docker-compose.yml, but found $DEPLOYMENT.docker-compose.json"
    COMPOSE_FILE="$DEPLOYMENT.docker-compose.json"
fi

CMD_BASE="docker compose -f docker-compose.yml -f $COMPOSE_FILE"

echo "starting $DEPLOYMENT"

# get the stragglers from the last run
echo "Cleaning up the last run..."
$CMD_BASE down
docker rm $(docker ps -aq)
# docker volume rm $(docker volume ls -q)

# make a driectory for jupyterhub shared mountss.
# The right way to do this is a named volume instead of a mapped volume,
# but there are permissions issues with that
mkdir -p ./jupyter_mounts/metaflow_metadata
chmod 777 -R ./jupyter_mounts

$CMD_BASE build
$CMD_BASE up
