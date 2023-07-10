from importer import dynamic_module_import
module = dynamic_module_import('generate_start_script')
import json
import pytest
class TestGenerateStart():

    @pytest.fixture
    def contextData(self):
       
        context = {
            "deployment_name": "test_context",
            "dns_base": "",
            "mod_base": "",
            "banner_color": "GREEN",
            "banner_text": "UNCLASSIFIED",
            "singleuser_type": "singleuser",
            "deploy_keycloak": True,
            "deploy_minio": True,
            "external_minio_url": "external/minio_url",
            "external_keycloak_url": "https://keycloak.opalacceptance.dso.mil",
            "keycloak_realm": "master"
        }

        return context

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
        actual = module.format_start_script(contextData)
        assert actual == expected