from importer import dynamic_module_import
module = dynamic_module_import('generate_env')
import json
import pytest

class TestGenerateEnv():

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


    def test_format_env_file(self):
        data = {
            'DEPLOYMENT_NAME': 'test_context', 
            'JUPYTERHUB_PORT': 443, 
            'KEYCLOAK_AUTH_SERVER_URL': 'https://keycloak/auth', 
            'KEYCLOAK_CALLBACK_URL': 'https://opal/services/opal-catalog/oauth_callback', 
            'JUPYTERHUB_API_URL': 'http://jupyterhub:8081/hub/api', 
            'OPAL_CATALOG_CALLBACK': 'https://opal/services/opal-catalog/oauth_callback', 
            'KEYCLOAK_JUPYTERHUB_OAUTH_CALLBACK_URL': 'https://opal/hub/oauth_callback', 
            'KEYCLOAK_JUPYTERHUB_AUTHORIZE_URL': 'https://keycloak/auth/realms/master/protocol/openid-connect/auth', 
            'KEYCLOAK_JUPYTERHUB_USERDATA_URL': 'https://keycloak/auth/realms/master/protocol/openid-connect/userinfo', 
            'KEYCLOAK_OPAL_API_URL': 'https://keycloak/auth/realms/master/protocol/openid-connect/token', 
            'DB_VENDOR': 'postgres', 
            'DB_ADDR': 'postgresql', 
            'DB_PORT': 5432, 
            'DB_DATABASE': 'keycloak-db', 
            'DB_USER': 'postgres',
            'DB_PASSWORD': 'postgres',
            'KEYCLOAK_USER': 'admin',
            'KEYCLOAK_PASSWORD' : 'opal',
            'MINIO_TEST_USER' : 'opaluser',
            'MINIO_TEST_USER_PASSWORD' : 'opalpassword',
            'MINIO_ROOT_USER' : 'opal-administrator',
            'MINIO_ROOT_PASSWORD' : 'opal_minio_password',
            'MINIO_IDENTITY_OPENID_CONFIG_URL' : 'https://keycloak/auth/realms/master/.well-known/openid-configuration',
            'MINIO_IDENTITY_OPENID_CLIENT_ID' : 'opal-jupyterhub',
            'MINIO_IDENTITY_OPENID_CLAIM_NAME' : 'policy',
            'MINIO_IDENTITY_OPENID_REDIRECT_URI' : 'https://minio/oauth_callback',
            'S3_ENDPOINT' : 'http://minio:9000',
            'MINIO_BROWSER_REDIRECT_URL' : 'https://minio',
            }
        expected = 'DEPLOYMENT_NAME=test_context\nJUPYTERHUB_PORT=443\nKEYCLOAK_AUTH_SERVER_URL=https://keycloak/auth\nKEYCLOAK_CALLBACK_URL=https://opal/services/opal-catalog/oauth_callback\nJUPYTERHUB_API_URL=http://jupyterhub:8081/hub/api\nOPAL_CATALOG_CALLBACK=https://opal/services/opal-catalog/oauth_callback\nKEYCLOAK_JUPYTERHUB_OAUTH_CALLBACK_URL=https://opal/hub/oauth_callback\nKEYCLOAK_JUPYTERHUB_AUTHORIZE_URL=https://keycloak/auth/realms/master/protocol/openid-connect/auth\nKEYCLOAK_JUPYTERHUB_USERDATA_URL=https://keycloak/auth/realms/master/protocol/openid-connect/userinfo\nKEYCLOAK_OPAL_API_URL=https://keycloak/auth/realms/master/protocol/openid-connect/token\nDB_VENDOR=postgres\nDB_ADDR=postgresql\nDB_PORT=5432\nDB_DATABASE=keycloak-db\nDB_USER=postgres\nDB_PASSWORD=postgres\nKEYCLOAK_USER=admin\nKEYCLOAK_PASSWORD=opal\nMINIO_TEST_USER=opaluser\nMINIO_TEST_USER_PASSWORD=opalpassword\nMINIO_ROOT_USER=opal-administrator\nMINIO_ROOT_PASSWORD=opal_minio_password\nMINIO_IDENTITY_OPENID_CONFIG_URL=https://keycloak/auth/realms/master/.well-known/openid-configuration\nMINIO_IDENTITY_OPENID_CLIENT_ID=opal-jupyterhub\nMINIO_IDENTITY_OPENID_CLAIM_NAME=policy\nMINIO_IDENTITY_OPENID_REDIRECT_URI=https://minio/oauth_callback\nS3_ENDPOINT=http://minio:9000\nMINIO_BROWSER_REDIRECT_URL=https://minio'
        actual = module.format_env_file(data)
        assert actual == expected
    
    def test_gen_secret(self):
        expected = 64
        actual = module.gen_secret()
        assert len(actual) == expected

    def test_keycloak_endpoint_deploykeycloak_false(self, contextData):
        contextData['deploy_keycloak'] = False
        expected = 'https://keycloak.opalacceptance.dso.mil'
        actual = module.keycloak_endpoint(contextData)
        assert actual == expected

    def test_keycloak_endpoint(self, contextData):
        expected = 'https://keycloak'
        actual = module.keycloak_endpoint(contextData)
        assert actual == expected

    def test_minio_endpoint(self, contextData):
        expected = ""
        actual = module.minio_endpoint(contextData)
        assert actual == expected

    def test_keycloak_env(self,contextData):
        expected = {
            "DB_VENDOR":"postgres",
            "DB_ADDR":"postgresql",
            "DB_PORT":5432,
            "DB_DATABASE":"keycloak-db",
            "DB_USER":"postgres",
            "DB_PASSWORD":"postgres",
            "KEYCLOAK_USER":"admin",
            "KEYCLOAK_PASSWORD":"opal",
            "MINIO_TEST_USER": "opaluser",
            "MINIO_TEST_USER_PASSWORD": "opalpassword"
        }
        actual = module.keycloak_env(contextData)
        assert actual == expected

    def test_keycloak_env_deployKeycloack_false(self,contextData):
        contextData['deploy_keycloak'] = False
        expected = {}
        actual = module.keycloak_env(contextData)
        assert actual == expected

    def test_minio_env(self, contextData):
        expected = {
            "MINIO_ROOT_USER":"opal-administrator",
            "MINIO_ROOT_PASSWORD":"opal_minio_password",
            "MINIO_IDENTITY_OPENID_CONFIG_URL":"https://keycloak/auth/realms/master/.well-known/openid-configuration",
            "MINIO_IDENTITY_OPENID_CLIENT_ID":"opal-jupyterhub",
            "MINIO_IDENTITY_OPENID_CLAIM_NAME":"policy",
            "MINIO_IDENTITY_OPENID_REDIRECT_URI":"https://minio/oauth_callback",
            "S3_ENDPOINT":"http://minio:9000",
            "MINIO_BROWSER_REDIRECT_URL":"https://minio",}
        actual = module.minio_env(contextData)
        assert actual == expected

    def test_minio_env_deployMinio_false(self, contextData):
        contextData['deploy_minio'] = False
        expected = {'S3_ENDPOINT': 'external/minio_url', 'MINIO_IDENTITY_OPENID_CONFIG_URL': 'https://keycloak/auth/realms/master/.well-known/openid-configuration', 'MINIO_IDENTITY_OPENID_CLIENT_ID': 'opal-jupyterhub', 'MINIO_IDENTITY_OPENID_CLAIM_NAME': 'policy'}
        actual = module.minio_env(contextData)
        assert actual == expected

    def test_generate_env_file(self,contextData):
        expected = {
            'DEPLOYMENT_NAME': 'test_context', 
            'JUPYTERHUB_PORT': 443, 
            'KEYCLOAK_AUTH_SERVER_URL': 'https://keycloak/auth', 
            'KEYCLOAK_CALLBACK_URL': 'https://opal/services/opal-catalog/oauth_callback', 
            'JUPYTERHUB_API_URL': 'http://jupyterhub:8081/hub/api', 
            'OPAL_CATALOG_CALLBACK': 'https://opal/services/opal-catalog/oauth_callback', 
            'KEYCLOAK_JUPYTERHUB_OAUTH_CALLBACK_URL': 'https://opal/hub/oauth_callback', 
            'KEYCLOAK_JUPYTERHUB_AUTHORIZE_URL': 'https://keycloak/auth/realms/master/protocol/openid-connect/auth', 
            'KEYCLOAK_JUPYTERHUB_USERDATA_URL': 'https://keycloak/auth/realms/master/protocol/openid-connect/userinfo', 
            'KEYCLOAK_OPAL_API_URL': 'https://keycloak/auth/realms/master/protocol/openid-connect/token', 
            'DB_VENDOR': 'postgres', 
            'DB_ADDR': 'postgresql', 
            'DB_PORT': 5432, 
            'DB_DATABASE': 'keycloak-db', 
            'DB_USER': 'postgres',
            'DB_PASSWORD': 'postgres',
            'KEYCLOAK_USER': 'admin',
            'KEYCLOAK_PASSWORD' : 'opal',
            'MINIO_TEST_USER' : 'opaluser',
            'MINIO_TEST_USER_PASSWORD' : 'opalpassword',
            'MINIO_ROOT_USER' : 'opal-administrator',
            'MINIO_ROOT_PASSWORD' : 'opal_minio_password',
            'MINIO_IDENTITY_OPENID_CONFIG_URL' : 'https://keycloak/auth/realms/master/.well-known/openid-configuration',
            'MINIO_IDENTITY_OPENID_CLIENT_ID' : 'opal-jupyterhub',
            'MINIO_IDENTITY_OPENID_CLAIM_NAME' : 'policy',
            'MINIO_IDENTITY_OPENID_REDIRECT_URI' : 'https://minio/oauth_callback',
            'S3_ENDPOINT' : 'http://minio:9000',
            'MINIO_BROWSER_REDIRECT_URL' : 'https://minio',
            }
        actual = module.generate_env_file(contextData)
        assert actual == expected