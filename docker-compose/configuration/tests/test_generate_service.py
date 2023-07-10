from importer import dynamic_module_import
module = dynamic_module_import('generate_service_file')
import json
import pytest

class TestGenerateService():

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

    def test_format_service_file(self,contextData):
        expected = """[Unit]
Description=OPAL Datascience Platform

[Service]
Type=simple
ExecStart=/bin/bash -c "cd \testDir -f docker-compose.yml -f test_context.docker-compose.json up --detach --remove-orphans"
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=OPAL

[Install]
WantedBy=multi-user.target
    """
        cwd = '\testDir'
        actual = module.format_service_file(contextData,cwd)
        assert actual == expected