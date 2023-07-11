from importer import dynamic_module_import
module = dynamic_module_import('generate_secrets')
import json
import pytest

class TestGenerateSecrets():

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

    def test_format_restart_script(self,contextData):
        expected = {
                "COOKIE_SECRET":64,
                "JUPYTERHUB_API_TOKEN":64,
                "KEYCLOAK_JUPYTERHUB_CLIENT_SECRET":64,
                "KEYCLOAK_MINIO_CLIENT_SECRET":64,
                "JUPYTERHUB_CRYPT_KEY":64,
                "KEYCLOAK_SECRET":64,
                "MINIO_IDENTITY_OPENID_CLIENT_SECRET":64,
                }
        actual = module.generate_secrets(contextData)
        for key, value in expected.items():
            assert len(actual[key]) == value

    def test_format_restart_script_deploy_keycloak_false(self,contextData):
        contextData['deploy_keycloak'] = False
        contextData["keycloak_secret"] = "0000000000000000000000000000000000000000000000000000000000000000"
        expected = {
                "COOKIE_SECRET":64,
                "JUPYTERHUB_API_TOKEN":64,
                "KEYCLOAK_JUPYTERHUB_CLIENT_SECRET":64,
                "KEYCLOAK_MINIO_CLIENT_SECRET":64,
                "JUPYTERHUB_CRYPT_KEY":64,
                "KEYCLOAK_SECRET":64,
                "MINIO_IDENTITY_OPENID_CLIENT_SECRET":64,
                }
        actual = module.generate_secrets(contextData)
        for key, value in expected.items():
            assert len(actual[key]) == value