import secrets
from generate_env import format_env_file, gen_secret

def generate_secrets(context):
    common_secret = gen_secret()
    if not context["deploy_keycloak"]:
        keycloak_secret = context["keycloak_secret"]
    else:
        keycloak_secret = common_secret
    return {
        "COOKIE_SECRET":common_secret,
        "JUPYTERHUB_API_TOKEN":gen_secret(),
        "KEYCLOAK_JUPYTERHUB_CLIENT_SECRET":keycloak_secret,
        "KEYCLOAK_MINIO_CLIENT_SECRET":keycloak_secret,
        "JUPYTERHUB_CRYPT_KEY":gen_secret(),
        "KEYCLOAK_SECRET":keycloak_secret,
        "MINIO_IDENTITY_OPENID_CLIENT_SECRET":keycloak_secret,
    }

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

    print(format_env_file(generate_secrets(context_data)))
