#! /bin/bash

# use the right python version
python3 --version 2&> /dev/null
if [[ $? -eq 0 ]]; then
    PYTHON=python3
else
    PYTHON=python
fi

# go to root of the opal-ops directory
cd $(dirname $0)/..

# do the thing

EXTRA_DATA='{
    "deployment_type":"docker-compose",
    "deployment_datetime":"'"$(date)"'"
}'

$PYTHON deployment-verification/generate_manifest.py \
    docker-compose/.env \
    docker-compose/.$1.env \
    docker-compose/out.json \
    .git \
    docker-compose/opal/.git \
    --extra "$EXTRA_DATA"\
    > docker-compose/$1_deployment_manifest.json