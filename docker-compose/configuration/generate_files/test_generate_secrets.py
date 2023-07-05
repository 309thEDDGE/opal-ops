import json
import generate_secrets
import pytest
class TestGenerateSecrets():

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
        actual = generate_secrets.generate_secrets(contextData)
        for key, value in expected.items():
            assert len(actual[key]) == value

    def test_format_restart_script_deploy_keycloak_false(self,contextData):
        contextData['deploy_keycloak'] = False
        expected = {
                "COOKIE_SECRET":64,
                "JUPYTERHUB_API_TOKEN":64,
                "KEYCLOAK_JUPYTERHUB_CLIENT_SECRET":64,
                "KEYCLOAK_MINIO_CLIENT_SECRET":64,
                "JUPYTERHUB_CRYPT_KEY":64,
                "KEYCLOAK_SECRET":64,
                "MINIO_IDENTITY_OPENID_CLIENT_SECRET":64,
                }
        actual = generate_secrets.generate_secrets(contextData)
        for key, value in expected.items():
            assert len(actual[key]) == value