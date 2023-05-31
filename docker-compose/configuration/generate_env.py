import secrets

def format_env_file(data:dict) -> str:
    return "\n".join([f"{k}={v}" for k,v in data.items()])

def gen_secret():
    return str(secrets.token_hex(nbytes=32))

def keycloak_endpoint(context) -> str:
    return (
        f"https://keycloak{context['mod_base']}" 
        if context['deploy_keycloak'] else
        context['external_keycloak_url']
    )

def minio_endpoint(context) -> str:
    return ""

def keycloak_env(context):
    return (
        {
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
        if context['deploy_keycloak'] else {}
    )

def minio_env(context):
    return (
        {
            "MINIO_ROOT_USER":"opal-administrator",
            "MINIO_ROOT_PASSWORD":"opal_minio_password",
            "S3_ENDPOINT":"http://minio:9000",
            "MINIO_BROWSER_REDIRECT_URL":f"https://minio{context['mod_base']}"
        }
        if context['deploy_minio'] else
        {
            "S3_ENDPOINT":f"{context['external_minio_url']}",
            "MINIO_IDENTITY_OPENID_CONFIG_URL":f"{keycloak_endpoint(context)}/auth/realms/{context['keycloak_realm']}/.well-known/openid-configuration",
            "MINIO_IDENTITY_OPENID_CLIENT_ID":"opal-jupyterhub",
            "MINIO_IDENTITY_OPENID_CLAIM_NAME":"policy"
        }
    )

def generate_env_file(context) -> dict:
    env = {
        # Other
        "DEPLOYMENT_NAME":f'{context["deployment_name"]}',

        # OpalCatalog fe/be environment variables
        "JUPYTERHUB_PORT":443,
        "KEYCLOAK_AUTH_SERVER_URL":f'{keycloak_endpoint(context)}/auth',
        "KEYCLOAK_CALLBACK_URL":f"https://opal{context['dns_base']}/services/opal-catalog/oauth_callback",
        "JUPYTERHUB_API_URL":"http://jupyterhub:8081/hub/api",

        # Jupyterhub environment variables
        "OPAL_CATALOG_CALLBACK":f"https://opal{context['dns_base']}/services/opal-catalog/oauth_callback",
        "KEYCLOAK_JUPYTERHUB_OAUTH_CALLBACK_URL":f"https://opal{context['dns_base']}/hub/oauth_callback",
        "KEYCLOAK_JUPYTERHUB_AUTHORIZE_URL":f"{keycloak_endpoint(context)}/auth/realms/{context['keycloak_realm']}/protocol/openid-connect/auth",
        "KEYCLOAK_JUPYTERHUB_USERDATA_URL":f"{keycloak_endpoint(context)}/auth/realms/{context['keycloak_realm']}/protocol/openid-connect/userinfo",
        "KEYCLOAK_OPAL_API_URL":f"{keycloak_endpoint(context)}/auth/realms/{context['keycloak_realm']}/protocol/openid-connect/token",
    } 
    env.update(keycloak_env(context))
    env.update(minio_env(context))
    return env

if __name__ == "__main__":
    import sys
    import json
    import os

    if len(sys.argv) <= 1:
        this_fname = os.path.basename(__file__)
        print(f"usage: python {this_fname} [context_file.json]")
        exit(1)

    with open(sys.argv[1]) as f:
        context_data = json.load(f)

    env_data = generate_env_file(context_data)

    print(format_env_file(env_data))
