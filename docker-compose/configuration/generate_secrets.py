import secrets
from generate_env import format_env_file, gen_secret

def generate_secrets():
    common_secret = gen_secret()
    return {
        "COOKIE_SECRET":common_secret,
        "JUPYTERHUB_API_TOKEN":gen_secret(),
        "KEYCLOAK_JUPYTERHUB_CLIENT_SECRET":common_secret,
        "KEYCLOAK_MINIO_CLIENT_SECRET":common_secret,
        "JUPYTERHUB_CRYPT_KEY":gen_secret(),
        "KEYCLOAK_SECRET":common_secret,
        "MINIO_IDENTITY_OPENID_CLIENT_SECRET":common_secret,
    }

if __name__ == "__main__":
    print(format_env_file(generate_secrets()))
