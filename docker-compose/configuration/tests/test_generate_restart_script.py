from importer import dynamic_module_import
module = dynamic_module_import('generate_restart_script')
import json
import pytest

class TestGenerateRestart():

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
            "external_minio_url": "external/minio_url",
            "external_keycloak_url": "https://externalURL"
        }"""
        context_json = json.loads(context)
        return context_json

    def test_format_restart_script(self,contextData):
        expected = """#!/bin/bash\n\n# this does a full restart of opal to avoid any odd quirks that may be caused by docker-compose restart\n\ndocker-compose -f docker-compose.yml -f test_context.docker-compose.json down\ndocker-compose -f docker-compose.yml -f test_context.docker-compose.json up -d\n    """
        actual = module.format_restart_script(contextData)
        assert actual == expected