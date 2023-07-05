import json
import generate_start_script
import pytest
class TestGenerateStart():

    @pytest.fixture
    def contextData(self):
       
        context = """{
            "deployment_name": "test_context",
            "dns_base": "",
            "mod_base": "",
            "banner_color": "Y",
            "banner_text": "orange",
            "singleuser_type": "singleuser",
            "deploy_keycloak": true,
            "deploy_minio": true,
            "keycloak_realm": "master",
            "keycloak_secret":"0000000000000000000000000000000000000000000000000000000000000000",    
            "external_minio_url": "external/minio_url",
            "external_keycloak_url": "https://externalURL"
        }"""
        context_json = json.loads(context)
        return context_json

    def test_format_start_script(self,contextData):
        expected = """#!/bin/bash

FILE=./.env.secrets

if test -f "$FILE"; then
    echo "Found secret file. Deploying"
else
    echo "Secrets missing. Please copy the secrets template file and fill out the values"
    echo "The template can be copied like so:"
    echo "cp .env.secrets_template .env.secrets"
    exit 1
fi

mkdir -p ./jupyter_mounts/metaflow_metadata
chmod 777 -R ./jupyter_mounts

docker-compose -f docker-compose.yml -f test_context.docker-compose.json build
docker-compose -f docker-compose.yml -f test_context.docker-compose.json up -d
    """
        actual = generate_start_script.format_start_script(contextData)
        assert actual == expected