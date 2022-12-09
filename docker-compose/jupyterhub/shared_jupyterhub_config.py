import os
from pathlib import Path
import requests
from oauthenticator.generic import GenericOAuthenticator

############################ ENVIRONMENT VARIABLES #####################################################################
# ENVIRONMENT VARIABLES FOR JUPYTERHUB, DOCKERSPAWNER AND OPAL-CATALOG EXTERNAL SERVICE
single_user_tip_image = "deploytime_singleuser"
jupyterhub_api_token = os.environ['JUPYTERHUB_API_TOKEN']
opal_catalog_callback = os.environ["OPAL_CATALOG_CALLBACK"]

# ENVIRONMENT VARIABLES FOR OPAL-SECRET-MANGER
minio_identity_openid_client_id=os.environ['MINIO_IDENTITY_OPENID_CLIENT_ID']
s3_endpoint = os.environ['S3_ENDPOINT']
keycloak_opal_api_url = os.environ['KEYCLOAK_OPAL_API_URL']
keycloak_minio_client_secret = os.environ['KEYCLOAK_MINIO_CLIENT_SECRET']

# ENVIRONMENT VARIABLES FOR GENERIC OAUTHENTICATOR KEYCLOAK CONFIGURATION
keycloak_jupyterhub_client_id = os.environ['KEYCLOAK_JUPYTERHUB_CLIENT_ID']
keycloak_jupyterhub_client_secret = os.environ['KEYCLOAK_JUPYTERHUB_CLIENT_SECRET']
keycloak_jupyterhub_oauth_callback_url = os.environ['KEYCLOAK_JUPYTERHUB_OAUTH_CALLBACK_URL']
keycloak_jupyterhub_authorize_url = os.environ['KEYCLOAK_JUPYTERHUB_AUTHORIZE_URL']
keycloak_jupyterhub_token_url  = keycloak_opal_api_url
keycloak_jupyterhub_userdata_url = os.environ['KEYCLOAK_JUPYTERHUB_USERDATA_URL']
keycloak_jupyterhub_username_key = os.environ['KEYCLOAK_JUPYTERHUB_USERNAME_KEY']

def set_shared_traitlets(c):
    c.JupyterHub.hub_ip = ' 0.0.0.0'
    c.JupyterHub.hub_connect_ip = 'jupyterhub'
    c.JupyterHub.spawner_class = 'cdsdashboards.hubextension.spawners.variabledocker.VariableDockerSpawner'

    c.Spawner.cmd=["jupyter-labhub"]
    c.Application.log_level = 'DEBUG'

    c.DockerSpawner.image = single_user_tip_image
    c.DockerSpawner.network_name = 'opal_default'

    c.DockerSpawner.remove = True
    c.DockerSpawner.debug = True

    config_path = os.path.join(
        os.environ["HOST_PATH"], 
        "jupyterhub", 
        "config"
    )

    metaflow_path = os.path.join(
        os.environ["HOST_PATH"],
        "jupyter_mounts",
        "metaflow_metadata"
    )

    # Persist Volumes
    metaflow_mount_path = "/opt/opal/metaflow-metadata"
    c.DockerSpawner.volumes = {
        'jupyterhub-user-{raw_username}':'/home/jovyan',
        config_path:"/opt/opal/conf",
        metaflow_path:metaflow_mount_path
    }

    # Commands to be executed inside container after container starts. Initiates conda and activates singleuser environment
    cmds = [
        "date >> /home/jovyan/startup.log",
        "conda init bash",
        "echo 'source /home/jovyan/.bashrc && conda activate singleuser' > /home/jovyan/.profile",
        "cp -r /opt/opal/conf/opalbanner /opt/conda/envs/singleuser/share/jupyter/labextensions",
        "bash /opt/opal/conf/init_banner.bash {} {}".format(os.environ['OPAL_BANNER_TEXT'], os.environ['OPAL_BANNER_COLOR']),
        "ln -sfn /opt/data/opal /home/jovyan/opal",
        "mv /home/jovyan/opal/START_HERE.ipynb /home/jovyan/",
        "mkdir -p /home/jovyan/.metaflowconfig",
        "envsubst < /opt/opal/conf/metaflow_config.json > /home/jovyan/.metaflowconfig/config.json",
        "python /opt/opal/conf/python_setup.py",
    ]

    messages = [
        "stamp current date",
        "init conda",
        "add conda activate to .profile",
        "move opalbanner files to singleuser extension directory",
        "change opalbanner color/text",
        "link opal directory",
        "copy START_HERE.ipynb to user home",
        "make metaflowconfig dir",
        "set metaflow config file",
        "run python setup script"
    ]

    with_debug_template = "( ({}) || echo 'Step {} Failed!' >> /home/jovyan/startup.log )"
    with_debug = [ with_debug_template.format(c, m) for c, m in zip(cmds, messages) ]

    cmd = "sh -c \"" + " && ".join(with_debug) + "\""
    c.DockerSpawner.post_start_cmd = cmd

    # Extra environment variables to set in single-user container. Needed for opal-secret-manager script.
    c.DockerSpawner.environment = {
        "MINIO_IDENTITY_OPENID_CLIENT_ID": minio_identity_openid_client_id,
        "KEYCLOAK_MINIO_CLIENT_SECRET": keycloak_minio_client_secret,
        "KEYCLOAK_OPAL_API_URL": keycloak_opal_api_url,
        "S3_ENDPOINT": s3_endpoint,
        "MINIO_IDENTITY_OPENID_CLIENT_ID": minio_identity_openid_client_id,
        "CATALOG_BACKEND_URL": "http://opalcatalog-be:9001/services/opal-catalog",
        "METAFLOW_DATASTORE_SYSROOT_LOCAL":metaflow_mount_path,
        "CHOWN_HOME":"yes",
        "CHOWN_HOME_OPTS":"-R",
        "CHOWN_EXTRA":"/home/jovyan",
    }

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

    # Keycloak GenericOauth
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


    ############################# LOAD USER ENVIRONMENT WITH MINIO CREDS ########################################
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

    class CustomAuthenticator(GenericOAuthenticator):
        async def pre_spawn_start(self, user, spawner):
            auth_state = await user.get_auth_state()

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

    c.JupyterHub.authenticator_class = CustomAuthenticator

    # Cdsdashboards stuff
    from cdsdashboards.app import CDS_TEMPLATE_PATHS
    from cdsdashboards.hubextension import cds_extra_handlers

    c.DockerSpawner.name_template = "{prefix}-{username}-{servername}"
    c.JupyterHub.template_paths = CDS_TEMPLATE_PATHS
    c.JupyterHub.extra_handlers = cds_extra_handlers
    c.JupyterHub.allow_named_servers = True
    c.CDSDashboardsConfig.builder_class = 'cdsdashboards.builder.dockerbuilder.DockerBuilder'

    # Group membership config
    c.GenericOAuthenticator.claim_groups_key = "groups"
    c.GenericOAuthenticator.allowed_groups = ["jupyterhub_staff"]
    c.GenericOAuthenticator.admin_groups = ["jupyterhub_admins"]
    c.GenericOAuthenticator.scope = ['openid', 'profile', 'roles']
