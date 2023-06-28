import json
import sys
import generate_docker_compose
from pathlib import Path
from datetime import datetime, timedelta

import pytest

class TestDeployment():

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
            "external_minio_url": "external/minio_url"
        }"""
        context_json = json.loads(context)
        return context_json

    def test_get_certs_path_keycloak(self,contextData):
        compose_root = Path(".")
        expected = compose_root / "./keycloak/certs/test_context"
        actual = generate_docker_compose.get_certs_path("keycloak", contextData)
        assert actual == expected

    def test_get_certs_path_notkeycloak_expected_files_not_matching(self,contextData):

        expectedfiles = ["test.crt", "test.key"]
        compose_root = Path(".")
        expected = compose_root / "./keycloak/certs/test_context"
        actual = generate_docker_compose.get_certs_path("keycloak", contextData, expectedfiles)
        assert actual == expected

    def test_get_certs_path_not_keycloak(self,contextData):
        expectedfiles = ["test.crt", "test.key"]
        compose_root = Path(".")
        expected = compose_root / "./keycloak1/certs/selfsigned"
        actual = generate_docker_compose.get_certs_path("keycloak1", contextData, expectedfiles)
        assert actual == expected

    def test_gen_selfsigned_keycloak_certs(self,contextData):
        compose_root = Path(".")
        expected = compose_root / "./keycloak/certs/test_context"
        actual = generate_docker_compose.gen_selfsigned_keycloak_certs(contextData)
        assert actual == expected

    def test_keycloak_link(self, contextData):
        expected = ['traefik:keycloak']
        actual = generate_docker_compose.keycloak_link(contextData)
        assert actual == expected

    def test_depends_on(self):
        expected = {'depends_on': {'keycloak1': {'condition':'service_healthy'}}}
        actual = generate_docker_compose.depends_on("keycloak1", "service_healthy")
        assert actual == expected

    minio_test_data = [
            ("test", True,'miniotest'),
            ("test1", False, 'external/minio_url'),
        ]

    @pytest.mark.parametrize("mod_base, deploy_minio, expected", minio_test_data)
    def test_minio_endpoint(self,contextData, mod_base,deploy_minio,expected):
        contextData['mod_base'] = mod_base
        contextData['deploy_minio'] = deploy_minio
        actual = generate_docker_compose.minio_endpoint(contextData)
        assert actual == expected

    def test_recursive_union(self,contextData):
        union_a = {"traefik":"keycloak"}
        union_b = {"deployment_name": "test_context",}
        expected = {
            "traefik":"keycloak",
            "deployment_name": "test_context",
        }
        actual = generate_docker_compose.recursive_union(union_a,union_b)
        assert actual == expected

    def test_keycloak_service(self, contextData):
        expected = { "keycloak": {
            "image": "${KEYCLOAK_IMAGE}",
            "depends_on": {
                "postgresql": {
                    "condition": "service_healthy"
                }
            },
            "volumes": [
                "./keycloak/certs/test_context/tls.key:/etc/x509/https/tls.key",
                "./keycloak/certs/test_context/tls.crt:/etc/x509/https/tls.crt"
            ],
            "env_file": [
                "./.env.secrets",
                "./.test_context.env",
                "./.env"
            ],
            "healthcheck": {
                "test": [
                    "CMD-SHELL",
                    "curl --fail http://localhost:9990/health"
                ],
                "interval": "60s",
                "timeout": "5s",
                "start_period": "60s",
                "retries": 10
            },
            "labels": [
                "traefik.enable=true",
                "traefik.http.routers.keycloak.rule=Host(`keycloak`)",
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
                "./.test_context.env",
                "./.env"
            ],
            "healthcheck": {
                "test": [
                    "CMD-SHELL",
                    "curl --fail http://localhost:9990/health"
                ],
                "interval": "60s",
                "timeout": "5s",
                "start_period": "60s",
                "retries": 10
            },
            "restart": "no",
            "volumes": [
                "./keycloak/keycloak_script.sh:/usr/local/bin/keycloak_script.sh"
            ],
            "entrypoint": [
                "sh",
                "/usr/local/bin/keycloak_script.sh"
            ]
        }}
        actual = generate_docker_compose.keycloak_service(contextData)
        assert actual == expected

    def test_minio_service(self, contextData):
        
        expected = {"minio": {
            "image": "${MINIO_IMAGE}",
            "command": "server --console-address \":9002\" --certs-dir /home/minio/certs /home/minio/data{1...4}",
            "env_file": [
                "./.env.secrets",
                "./.test_context.env",
                "./.env"
            ],
            "volumes": [
                "./keycloak/certs/test_context/tls.crt:/home/minio/certs/CAs/tls.crt"
            ],
            "links": [
                "traefik:keycloak"
            ],
            "labels": [
                "traefik.enable=true",
                "traefik.http.routers.minio.rule=Host(`minio`)",
                "traefik.http.routers.minio.entrypoints=websecure",
                "traefik.http.services.minio.loadbalancer.server.port=9002",
                "traefik.http.routers.minio.service=minio",
                "traefik.http.routers.minio_api.rule=Host(`minio_api`)",
                "traefik.http.routers.minio_api.entrypoints=websecure",
                "traefik.http.services.minio_api.loadbalancer.server.port=9000",
                "traefik.http.routers.minio_api.service=minio"
            ],
            "restart": "always"
        }
    }
        actual = generate_docker_compose.minio_service(contextData)
        assert actual == expected

    def test_add_depends_to_service(self, contextData):
        jupyter_service = {
        "build": {
            "args": {
                "OPAL_BANNER_COLOR": contextData['banner_color'],
                "OPAL_BANNER_TEXT": contextData['banner_text']
            }
        },
        "volumes": [
            "./jupyterhub/dev.jupyterhub_config.py:/home/jovyan/jupyterhub_config.py"
        ],
        "env_file": [
            deployment_env
        ],
        "environment": [
            f"OPAL_BANNER_COLOR={contextData['banner_color']}",
            f"OPAL_BANNER_TEXT='{contextData['banner_text']}'"
        ],
        "links": keycloak_link(contextData),
        "labels": [
            f"traefik.http.routers.jupyterhub.rule=Host(`opal{contextData['dns_base']}`)",
            f"traefik.http.routers.jupyterhub_api.rule=Host(`jupyterhub_api{contextData['mod_base']}`)"
        ]
    }
        expected = ""
        actual = generate_docker_compose.add_depends_to_service(jupyter_service,generate_docker_compose.depends_on("keycloak", "service_healthy")))
        assert actual == expected