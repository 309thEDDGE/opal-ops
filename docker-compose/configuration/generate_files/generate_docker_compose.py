from pathlib import Path
import subprocess
import tempfile
import shutil
import ssl

cert_files = {
    "keycloak":["tls.crt", "tls.key"]
}
def get_certs_path(service, context, expected_files=[]):
    if not expected_files:
        expected_files = cert_files[service]

    compose_root = Path(".")
    expected_certs_dir = compose_root / service / "certs" / context['deployment_name']

    dir_exists = expected_certs_dir.exists()
    certs_exist = all([ (expected_certs_dir / e).exists() for e in expected_files ])

    has_certs = dir_exists and certs_exist

    if has_certs:
        return expected_certs_dir
    elif service == "keycloak":
        return gen_selfsigned_keycloak_certs(context)
    else:
        return compose_root/service/"certs"/"selfsigned"

def gen_selfsigned_keycloak_certs(context):

    # use a temporary file for the config input to openssl
    config = [
        "[req]",
        "distinguished_name=req",
        "[san]",
        f"subjectAltName=DNS:*{context['mod_base']}"
    ]

    # NOTE: this will NOT work on windows
    # But we don't plan to deploy Opal on windows anyways.
    with tempfile.NamedTemporaryFile(mode="w") as f:
        f.write("\n".join(config))
        f.flush()

        # generate the certificates
        thing = subprocess.check_output([
            "openssl", "req", "-new",
            "-newkey", "rsa:2048", "-days", "365",
            "-nodes", "-x509", 
            "-subj", f"/CN=*.{context['mod_base']}",
            "-extensions", "san",
            "-config", f.name,
            "-keyout", "tls.key",
            "-out", "tls.crt"
        ])

    # make new directory for this deployment's certs
    compose_root = Path(".")
    new_path = compose_root/"keycloak"/"certs"/context['deployment_name']
    new_path.mkdir(parents=True, exist_ok=True)

    # move generated files to new deployment cert directory
    shutil.move("tls.crt", new_path/"tls.crt")
    shutil.move("tls.key", new_path/"tls.key")

    # calling function needs the folder directory
    return new_path


def get_external_keycloak_cert(context: dict, write_path):
    # seems ssl in some python versions (maybe OS-dependent?) don't work if the protocol is in the URL
    no_protocol = context['external_keycloak_url'].replace('https://','')
    keycloak_public_cert = ssl.get_server_certificate((no_protocol,443))
    cert_path = write_path/"kc.crt"
    with open(cert_path, "w") as f:
        f.write(keycloak_public_cert)


def keycloak_link(context: dict) -> list:
    return (
        [f"traefik:keycloak{context['mod_base']}"]
        if context['deploy_keycloak']
        else []
    )

def depends_on(service, condition):
    return {
        "depends_on": {
            service: {"condition": condition}
        }
    }

def minio_endpoint(context) -> str:
    return (
        f"minio{context['mod_base']}"
        if context['deploy_minio'] else
        context['external_minio_url']
    )

# recursively merges dictionaries
def recursive_union(dict_a, dict_b):
    # start with a simple merge/union/whatever
    out = dict_a.copy()
    out.update(dict_b)

    # for all the same keys
    for k in set(dict_a.keys()).intersection(set(dict_b.keys())):
        a = dict_a[k]
        b = dict_b[k]
        
        # check types
        if not isinstance(a, type(b)):
            raise TypeError(f"Can't union type {type(a)} with {type(b)}")
        
        # concatenate lists
        if isinstance(a, list):
            out[k] = a + b
        # merge dictionaries
        elif isinstance(a, dict):
            out[k] = recursive_union(a, b)
        # give up on everything else
        else:
            raise TypeError(f"Can't union type {type(a)} with {type(b)}")

    return out

def keycloak_service(context: dict) -> dict:
    deployment_env = f"./.{context['deployment_name']}.env"
    keycloak_certs = get_certs_path("keycloak", context)

    return ({
        "keycloak": {
            "image": "${KEYCLOAK_IMAGE}",
            "command": "start",
            "depends_on": {
                "postgresql": {
                    "condition": "service_healthy"
                }
            },
            "volumes": [
                f"./{keycloak_certs / 'tls.key'}:/etc/x509/https/tls.key",
                f"./{keycloak_certs / 'tls.crt'}:/etc/x509/https/tls.crt",
                "keycloak_log_storage:/logs"
            ],
            "env_file": [
                "./.env.secrets",
                deployment_env,
                "./.env"
            ],
            "healthcheck": {
                "test": ["CMD-SHELL", "curl --fail http://localhost:9000/health"],
                "interval": "60s",
                "timeout": "5s",
                "start_period": "60s",
                "retries": 10,
            },
            "labels": [
                "traefik.enable=true",
                f"traefik.http.routers.keycloak.rule=Host(`keycloak{context['mod_base']}`)",
                "traefik.http.routers.keycloak.entrypoints=websecure",
                "traefik.http.services.keycloak.loadbalancer.server.port=8080",
                "traefik.http.routers.keycloak.service=keycloak"
            ],
            "restart": "always"
        },
        "keycloak_setup": {
            "image": "${KEYCLOAK_IMAGE}",
            "depends_on": {
                "keycloak": {
                    "condition": "service_healthy"
                }
            },
            "env_file": [
                "./.env.secrets",
                deployment_env,
                "./.env"
            ],
            "healthcheck": {
                "test": ["CMD-SHELL", "curl --fail http://localhost:9990/health"],
                "interval": "60s",
                "timeout": "5s",
                "start_period": "60s",
                "retries": 10,
            },
            "restart": "no",
            "volumes": [
                "./keycloak/keycloak_script.sh:/usr/local/bin/keycloak_script.sh"
            ],
            "entrypoint": [
                "sh",
                "/usr/local/bin/keycloak_script.sh"
            ]
        }
    } if context['deploy_keycloak'] else {}
    )


def minio_service(context:dict) -> dict:
    deployment_env = f"./.{context['deployment_name']}.env"
    keycloak_certs = get_certs_path("keycloak", context)
    if context["deploy_keycloak"]:
        volume_string = f"./{keycloak_certs / 'tls.crt'}:/home/minio/certs/CAs/tls.crt"
    else:
        volume_string = f"./{keycloak_certs / 'kc.crt'}:/home/minio/certs/CAs/tls.crt"

    return {
        "minio": {
            "image": "${MINIO_IMAGE}",
            "command": "server --console-address \":9002\" --certs-dir /home/minio/certs /home/minio/data{1...4}",
            "env_file": [
                "./.env.secrets",
                deployment_env,
                "./.env"
            ],
            "volumes": [
                "minio_storage:/home/minio/",
                volume_string
            ],
            "ports": [
                "9000:9000"
            ],
            "healthcheck":{
                "test": [
                    "CMD",
                    "curl",
                    "-f",
                    "-k",
                    "http://localhost:9000/minio/health/live"
                ],
                "interval": "30s",
                "timeout": "20s",
                "retries": 3
            },
            "links": keycloak_link(context),
            "labels": [
                "traefik.enable=true",
                f"traefik.http.routers.minio.rule=Host(`minio{context['mod_base']}`)",
                "traefik.http.routers.minio.entrypoints=websecure",
                "traefik.http.services.minio.loadbalancer.server.port=9002",
                "traefik.http.routers.minio.service=minio",
                f"traefik.http.routers.minio_api.rule=Host(`minio_api{context['mod_base']}`)",
                "traefik.http.routers.minio_api.entrypoints=websecure",
                "traefik.http.services.minio_api.loadbalancer.server.port=9000",
                "traefik.http.routers.minio_api.service=minio"
            ],
            "restart": "always"
        }
    } if context['deploy_minio'] else {}

def add_depends_to_service(service_dict, arg):
    if len(arg) == 0:
        return

    if not "depends_on" in service_dict:
        service_dict["depends_on"] = {}

    service_dict["depends_on"].update(arg["depends_on"])

def generate_docker_compose(context: dict) -> dict:
    deployment_env = f"./.{context['deployment_name']}.env"
    keycloak_certs = get_certs_path("keycloak", context)
    if not context["deploy_keycloak"]: get_external_keycloak_cert(context, keycloak_certs)

    jupyter_service = {
        "build": {
            "args": {
                "OPAL_BANNER_COLOR": context['banner_color'],
                "OPAL_BANNER_TEXT": context['banner_text']
            }
        },
        "volumes": [
            "./jupyterhub/dev.jupyterhub_config.py:/home/jovyan/jupyterhub_config.py"
        ],
        "env_file": [
            deployment_env
        ],
        "environment": [
            f"OPAL_BANNER_COLOR={context['banner_color']}",
            f"OPAL_BANNER_TEXT='{context['banner_text']}'"
        ],
        "links": keycloak_link(context),
        "labels": [
            f"traefik.http.routers.jupyterhub.rule=Host(`opal{context['dns_base']}`)",
            f"traefik.http.routers.jupyterhub_api.rule=Host(`jupyterhub_api{context['mod_base']}`)"
        ]
    }

    if context["deploy_keycloak"]:
        add_depends_to_service(jupyter_service, depends_on("keycloak", "service_healthy"))

    traefik_service = {
        "volumes": [
            f"./{keycloak_certs}:/etc/traefik/certs/"
        ],
        "env_file": [
            deployment_env
        ]
    }
    
    if context["deploy_keycloak"]:
        add_depends_to_service(traefik_service, depends_on("keycloak", "service_healthy"))
        add_depends_to_service(traefik_service, depends_on("keycloak_setup", "service_started"))

    services = {
        "postgresql": {
            "env_file": [
                deployment_env
            ]
        },
        "singleuser": {
            "build": {
                "context": ".",
                "dockerfile": f"./singleuser/Dockerfile",
                "args": {
                    "OPAL_BANNER_COLOR": context['banner_color'],
                    "OPAL_BANNER_TEXT": context['banner_text']
                }
            }
        },
        "jupyterhub": jupyter_service,
        "traefik": traefik_service
    }

    services.update(keycloak_service(context))
    services.update(minio_service(context))

    compose = {"version": "3.9",
           "services": services
           }

    if context["deploy_minio"]:
        vols = {"volumes": {"minio_storage": None}}
        compose.update(vols)

    return compose

if __name__ == "__main__": # pragma: no cover
    import sys
    import json
    import os

    if len(sys.argv) <= 1:
        this_fname = os.path.basename(__file__)
        print(f"usage: python {this_fname} [context_file.json]")
        exit(1)

    with open(sys.argv[1]) as f:
        context_data = json.load(f)

    compose_data = generate_docker_compose(context_data)

    print(json.dumps(compose_data, indent=4))
