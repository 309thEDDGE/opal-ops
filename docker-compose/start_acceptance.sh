#!/bin/bash

FILE=./.env.secrets

if test -f "$FILE"; then
    echo "Found secret file. Deploying"
else
    echo "Secrets missing. Please copy the secrets template file and fill out the values"
    echo "The template can be copied like so:"
    echo "cp .env.secrets_template .env.secrets"
    exit 1
fi

LATEST_TAG=$(git tag -l --sort=refname | tail -n 1)
git checkout master
git checkout "$LATEST_TAG"

docker-compose -f docker-compose.yml -f acceptance.docker-compose.yml build
docker-compose -f docker-compose.yml -f acceptance.docker-compose.yml up -d

echo "OPAL deployed with latest tag $LATEST_TAG"
