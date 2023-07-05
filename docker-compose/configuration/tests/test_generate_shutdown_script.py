from importer import dynamic_module_import
module = dynamic_module_import('generate_shutdown_script')
import json
import pytest

class TestGenerateShutdown():

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

    def test_format_shutdown_script(self,contextData):
        expected = """#!/bin/bash

docker-compose -f docker-compose.yml -f test_context.docker-compose.json down
    """
        actual = module.format_shutdown_script(contextData)
        assert actual == expected