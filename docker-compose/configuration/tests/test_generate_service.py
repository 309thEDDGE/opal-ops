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
        compose = "docker-compose.yml"
        module.COMPOSE = compose
        expected = """[Unit]\nDescription=OPAL Datascience Platform\nRequires=docker.service\n\n[Service]\nType=oneshot\nRemainAfterExit=yes\nTimeoutStopSec=120\nExecStart=/bin/bash -c "cd \testDir && docker-compose.yml -f docker-compose.yml -f test_context.docker-compose.json down --remove-orphans && docker-compose.yml -f docker-compose.yml -f test_context.docker-compose.json up --detach --remove-orphans"\nExecStop=/bin/bash -c "cd \testDir && docker-compose.yml -f docker-compose.yml -f test_context.docker-compose.json down --remove-orphans"\nStandardOutput=syslog\nStandardError=syslog\nSyslogIdentifier=OPAL\n\n[Install]\nWantedBy=multi-user.target\n    """
        cwd = '\testDir'
        actual = module.format_service_file(contextData,cwd)
        assert actual == expected