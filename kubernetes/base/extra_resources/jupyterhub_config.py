import os
from oauthenticator.generic import GenericOAuthenticator
import requests
# import re
# import sys

# from tornado.httpclient import AsyncHTTPClient
# from kubernetes import client
# from jupyterhub.utils import url_path_join

c.JupyterHub.spawner_class = 'kubespawner.KubeSpawner'

# Connect to a proxy running in a different pod
c.ConfigurableHTTPProxy.api_url = 'http://{}:{}'.format(os.environ['PROXY_API_SERVICE_HOST'], int(os.environ['PROXY_API_SERVICE_PORT']))
c.ConfigurableHTTPProxy.should_start = False

# proxy routing
c.JupyterHub.last_activity_interval = 60
c.JupyterHub.ip = os.environ['PROXY_PUBLIC_SERVICE_HOST']
c.JupyterHub.port = int(os.environ['PROXY_PUBLIC_SERVICE_PORT'])

# the hub should listen on all interfaces, so the proxy can access it
c.JupyterHub.hub_ip = '0.0.0.0'

# set the user's server image
c.KubeSpawner.image_pull_policy = "Never"
c.KubeSpawner.image_pull_secrets = ["regcred"]
# c.KubeSpawner.image = "registry.il2.dso.mil/skicamp/project-opal/tip:f970c010"
c.KubeSpawner.image = os.environ["SINGLE_USER_IMAGE"]

# inherit some jupyterhub environment variables
c.KubeSpawner.env_keep = [
    "OPAL_BANNER_TEXT",
    "OPAL_BANNER_COLOR",
    "MINIO_IDENTITY_OPENID_CLIENT_ID",
    "KEYCLOAK_MINIO_CLIENT_SECRET",
    "KEYCLOAK_OPAL_API_URL",
    # "KEYCLOAK_JUPYTERHUB_CLIENT_ID",
    # "KEYCLOAK_JUPYTERHUB_OAUTH_URL",
    # "KEYCLOAK_JUPYTERHUB_USERDATA_URL",
    # "KEYCLOAK_JUPYTERHUB_USERNAME_KEY"
]

metaflow_mount_path = "/opt/opal/metaflow-metadata"
# add some extra environment variables
c.KubeSpawner.environment = {
    "S3_ENDPOINT": "http://minio:9000",
    "USERNAME": "jovyan",
    "METAFLOW_DATASTORE_SYSROOT_LOCAL":metaflow_mount_path,
    "CATALOG_BACKEND_URL": "http://opalcatalog-be:9001/services/opal-catalog",
}

# assign a security context for write permissions to
# the attached volumes
c.KubeSpawner.fs_gid = 100
c.KubeSpawner.uid = 1000

# # Mount volume for storage
pvc_name_template = 'claim-{username}'
c.KubeSpawner.pvc_name_template = pvc_name_template

c.KubeSpawner.storage_pvc_ensure = True
c.KubeSpawner.storage_class = 'standard'
c.KubeSpawner.storage_access_modes = ['ReadWriteOnce']
c.KubeSpawner.storage_capacity = '1Gi'

# Add volumes to singleuser pods
c.KubeSpawner.volumes = [
    {
        'name': "config-tar",
        "configMap":{
            "name": "jupyterhub-config"
        }
    },
    {
        'name': "startup-script",
        "configMap": {
            "name": "jupyterhub-startup-script",
            "defaultMode": 0o755 # octal permission number
        }
    },
    {
        'name': "metaflow-store",
        "persistentVolumeClaim": {
            "claimName": "metaflow-datastore"
        }
    }
]

c.KubeSpawner.volume_mounts = [
    {
        'mountPath': '/tmp/tars/jhub-conf.tar',
        'subPath': "jupyterhub-conf-dir.tar",
        'name': "config-tar"
    },
    {
        'mountPath': '/tmp/startup_script.bash',
        "subPath": "startup_script.bash",
        "name": "startup-script"
    },
    {
        'mountPath': metaflow_mount_path,
        "name": "metaflow-store",
        "readOnly": False
    }
]

# set the startup bash script
c.KubeSpawner.cmd = "/tmp/startup_script.bash"

# # Gives spawned containers access to the API of the hub

c.JupyterHub.hub_connect_ip = os.environ['HUB_SERVICE_HOST']
c.JupyterHub.hub_connect_port = int(os.environ['HUB_SERVICE_PORT'])

# Authentication
def get_minio_creds(keycloak_access_token):
    body = {
            "Action": "AssumeRoleWithWebIdentity",
            "WebIdentityToken": keycloak_access_token,
            "Version": "2011-06-15",
            # "DurationSeconds": 604800, # This should pick up the value specified by keycloak if left blank
            }
    r = requests.post(s3_endpoint, data=body)

    if r.status_code != 200:
        raise Exception(f"***Minio sts failed***\nkeycloak access token: {keycloak_access_token}\nresponse for sts request:\n{r}\ntext response:\n{r.text}")
    xml = r.text
    access_key_id = xml.split("<AccessKeyId>")[1].split("</AccessKeyId>")[0]
    secret_access_key = xml.split("<SecretAccessKey>")[1].split("</SecretAccessKey>")[0]
    session_token = xml.split("<SessionToken>")[1].split("</SessionToken>")[0]

    return access_key_id, secret_access_key, session_token

# authenticator class
s3_endpoint = os.environ['S3_ENDPOINT']

class CustomAuthenticator(GenericOAuthenticator):
    async def pre_spawn_start(self, user, spawner):
        try:
            auth_state = await user.get_auth_state()
        except:
            print("Minio STS Failed")
            auth_state = None

        if not auth_state:
            # user has no auth state
            return

        access_token = auth_state['access_token']

        access_key_id, secret_access_key, session_token = get_minio_creds(access_token)

        # define environment variables
        spawner.environment['S3_KEY'] = access_key_id
        spawner.environment['S3_SECRET'] = secret_access_key
        spawner.environment['S3_SESSION'] = session_token

        # define some more environment variables - these are necessary for metaflow
        spawner.environment['AWS_ACCESS_KEY_ID'] = access_key_id
        spawner.environment['AWS_SECRET_ACCESS_KEY'] = secret_access_key
        spawner.environment['AWS_SESSION_TOKEN'] = session_token
        spawner.environment['USERNAME'] = 'jovyan'

# ENVIRONMENT VARIABLES FOR GENERIC OAUTHENTICATOR KEYCLOAK CONFIGURATION
keycloak_jupyterhub_client_id = os.environ['KEYCLOAK_JUPYTERHUB_CLIENT_ID']
keycloak_jupyterhub_client_secret = os.environ['KEYCLOAK_JUPYTERHUB_CLIENT_SECRET']
keycloak_jupyterhub_oauth_callback_url = os.environ['KEYCLOAK_JUPYTERHUB_OAUTH_CALLBACK_URL']
keycloak_jupyterhub_authorize_url = os.environ['KEYCLOAK_JUPYTERHUB_AUTHORIZE_URL']
keycloak_opal_api_url = os.environ['KEYCLOAK_OPAL_API_URL']
keycloak_jupyterhub_userdata_url = os.environ['KEYCLOAK_JUPYTERHUB_USERDATA_URL']
keycloak_jupyterhub_username_key = os.environ['KEYCLOAK_JUPYTERHUB_USERNAME_KEY']

c.GenericOAuthenticator.login_service = 'keycloak'
c.GenericOAuthenticator.userdata_params = {"state": "state"}
c.GenericOAuthenticator.client_id = keycloak_jupyterhub_client_id
c.GenericOAuthenticator.client_secret = keycloak_jupyterhub_client_secret
c.GenericOAuthenticator.tls_verify = False
c.GenericOAuthenticator.oauth_callback_url = keycloak_jupyterhub_oauth_callback_url
c.GenericOAuthenticator.authorize_url = keycloak_jupyterhub_authorize_url
c.GenericOAuthenticator.token_url = keycloak_opal_api_url
c.GenericOAuthenticator.username_key = keycloak_jupyterhub_username_key
c.GenericOAuthenticator.userdata_url = keycloak_jupyterhub_userdata_url
c.GenericOAuthenticator.enable_auth_state = True
c.GenericOAuthenticator.refresh_pre_spawn = True

c.JupyterHub.authenticator_class = CustomAuthenticator

# Group membership config
c.OAuthenticator.claim_groups_key = "groups"
c.OAuthenticator.allowed_groups = ["jupyterhub_staff"]
c.OAuthenticator.admin_groups = ["jupyterhub_admins"]
c.OAuthenticator.scope = ['openid', 'profile', 'roles']

########## extra services ##########

jupyterhub_api_token = os.environ['JUPYTERHUB_API_TOKEN']
opal_catalog_callback = os.environ["OPAL_CATALOG_CALLBACK"]

c.JupyterHub.services = [
    {
        'name': 'opal-catalog',
        'api_token': jupyterhub_api_token,
        'url': 'http://opalcatalog-fe:9003/services/opal-catalog',
        'oauth_client_id': "service-opal-catalog-be",
        'oauth_redirect_uri': opal_catalog_callback,
        'admin': True,
        'oauth_no_confirm': True
    }
]

# Cdsdashboards stuff
from cdsdashboards.app import CDS_TEMPLATE_PATHS
from cdsdashboards.hubextension import cds_extra_handlers

c.DockerSpawner.name_template = "{prefix}-{username}-{servername}"
c.JupyterHub.template_paths = CDS_TEMPLATE_PATHS
c.JupyterHub.extra_handlers = cds_extra_handlers
c.JupyterHub.allow_named_servers = True
c.CDSDashboardsConfig.builder_class = 'cdsdashboards.builder.dockerbuilder.DockerBuilder'
