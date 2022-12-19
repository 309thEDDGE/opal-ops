#! /bin/bash

# use the right python version
python3 --version
if [[ $? -eq 0 ]]; then
    PYTHON=python3
else
    PYTHON=python
fi

# go to root of the opal-ops directory
cd $(dirname $0)/..

# do the thing

$PYTHON deployment-verification/generate_manifest.py \
    docker-compose/.env \
    docker-compose/.$1.env \
    docker-compose/out.json