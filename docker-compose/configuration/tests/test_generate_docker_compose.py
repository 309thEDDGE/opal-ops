import json
from importer import dynamic_module_import
module = dynamic_module_import('generate_docker_compose')
from pathlib import Path

import responses

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
            "external_minio_url": "external/minio_url",
            "external_keycloak_url": "https://keycloak.opalacceptance.dso.mil"
        }"""
        context_json = json.loads(context)
        return context_json

    def test_get_certs_path_keycloak(self,contextData):
        compose_root = Path(".")
        expected = compose_root / "./keycloak/certs/test_context"
        actual = module.get_certs_path("keycloak", contextData)
        assert actual == expected

    def test_get_certs_path_notkeycloak_expected_files_not_matching(self,contextData):

        expectedfiles = ["test.crt", "test.key"]
        compose_root = Path(".")
        expected = compose_root / "./keycloak/certs/test_context"
        actual = module.get_certs_path("keycloak", contextData, expectedfiles)
        assert actual == expected

    def test_get_certs_path_not_keycloak(self,contextData):
        expectedfiles = ["test.crt", "test.key"]
        compose_root = Path(".")
        expected = compose_root / "./keycloak1/certs/selfsigned"
        actual = module.get_certs_path("keycloak1", contextData, expectedfiles)
        assert actual == expected

    def test_gen_selfsigned_keycloak_certs(self,contextData):
        compose_root = Path(".")
        expected = compose_root / "./keycloak/certs/test_context"
        actual = module.gen_selfsigned_keycloak_certs(contextData)
        assert actual == expected

    @responses.activate
    def test_get_external_keycloak_cert(self,contextData):
        response = responses.Response(
            method=responses.GET,
            url=contextData["external_keycloak_url"],
            body="-----BEGIN CERTIFICATE-----\naskjdajsdkjaksljdlkajslkdjaljsdjkdhkjhajkfhd\n-----END CERTIFICATE-----"
        )
        responses.add(response)
        compose_root = Path(".")
        expectedPath = compose_root / "./keycloak/certs/test_context"
        expected_begin = '-----BEGIN CERTIFICATE-----\n'
        expected_end = '-----END CERTIFICATE-----\n'
        module.get_external_keycloak_cert(contextData, expectedPath)
        actual_begin = None
        actual_end = None
        with open(f"{expectedPath}/kc.crt", 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                actual_begin = lines[0]
                actual_end = lines[-1]
        assert actual_begin == expected_begin
        assert actual_end == expected_end

    def test_keycloak_link(self, contextData):
        expected = ['traefik:keycloak']
        actual = module.keycloak_link(contextData)
        assert actual == expected

    def test_depends_on(self):
        expected = {'depends_on': {'keycloak1': {'condition':'service_healthy'}}}
        actual = module.depends_on("keycloak1", "service_healthy")
        assert actual == expected

    minio_test_data = [
            ("test", True,'miniotest'),
            ("test1", False, 'external/minio_url'),
        ]

    @pytest.mark.parametrize("mod_base, deploy_minio, expected", minio_test_data)
    def test_minio_endpoint(self,contextData, mod_base,deploy_minio,expected):
        contextData['mod_base'] = mod_base
        contextData['deploy_minio'] = deploy_minio
        actual = module.minio_endpoint(contextData)
        assert actual == expected

    def test_recursive_union_no_common_key(self,contextData):
        union_a = {"traefik":"keycloak"}
        union_b = {"deployment_name": "test_context",}
        expected = {
            "traefik":"keycloak",
            "deployment_name": "test_context",
        }
        actual = module.recursive_union(union_a,union_b)
        assert actual == expected

    def test_recursive_union_duplicate_keys(self):
        union_a = {"traefik":["keycloak", "test_context"]}
        union_b = {"traefik": ["keycloak1", "test_context1"],}
        expected = {
            "traefik":["keycloak", "test_context", "keycloak1", "test_context1"]
        }
        actual = module.recursive_union(union_a,union_b)
        assert actual == expected

    def test_recursive_union_duplicate_keys_different_types(self):
        union_a = {"traefik": False}
        union_b = {"traefik": "False"}

        with pytest.raises(TypeError) as _:
            module.recursive_union(union_a,union_b)

    def test_recursive_union_duplicate_keys_same_types_no_list_or_dict(self):
        union_a = {"traefik": "False"}
        union_b = {"traefik": "False"}

        with pytest.raises(TypeError) as _:
            module.recursive_union(union_a,union_b)

    list_data = [
        ({"traefik": ["a", "a1"]}, {"traefik": ["b", "b1"]},{"traefik": ["a", "a1", "b", "b1"]}),
        ({"traefik": ["a", "a1"]}, {"traefik": [True, False]},{"traefik": ["a", "a1", True, False]}),
        ({"traefik": {"a": "a1"}}, {"traefik": [True, False]}, "RAISE ERROR"),
        ({"traefik": {"a": [True, False]}}, {"traefik": {"a": [False]}}, {"traefik": {"a": [True, False, False]}})
    ]

    @pytest.mark.parametrize("union_a, union_b, expected", list_data)
    def test_recursive_union_duplicate_keys_list_dict(self, union_a, union_b, expected):
        
        if expected == "RAISE ERROR":
            with pytest.raises(TypeError) as _:
                module.recursive_union(union_a, union_b)
            return

        actual = module.recursive_union(union_a,union_b)
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
        actual = module.keycloak_service(contextData)
        assert actual == expected

    minioData = [
        (True, 'tls.crt'),
        (False, 'kc.crt')
    ]

    @pytest.mark.parametrize("deployKeycloakVal, certValue", minioData)
    def test_minio_service(self, contextData, deployKeycloakVal, certValue):

        contextData['deploy_keycloak'] = deployKeycloakVal
        
        expected = {"minio": {
            "image": "${MINIO_IMAGE}",
            "command": "server --console-address \":9002\" --certs-dir /home/minio/certs /home/minio/data{1...4}",
            "env_file": [
                "./.env.secrets",
                "./.test_context.env",
                "./.env"
            ],
            "volumes": [
                f"./keycloak/certs/test_context/{certValue}:/home/minio/certs/CAs/tls.crt"
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
        actual = module.minio_service(contextData)
        assert actual == expected

    def test_add_depends_to_service(self, contextData):
        deployment_env = f"./.{contextData['deployment_name']}.env"
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
        "links": module.keycloak_link(contextData),
        "labels": [
            f"traefik.http.routers.jupyterhub.rule=Host(`opal{contextData['dns_base']}`)",
            f"traefik.http.routers.jupyterhub_api.rule=Host(`jupyterhub_api{contextData['mod_base']}`)"
        ]
    }
        expected = {'keycloak': {'condition': 'service_healthy'}}
        actual = module.add_depends_to_service(jupyter_service,module.depends_on("keycloak", "service_healthy"))
        assert jupyter_service["depends_on"] == expected

    def test_add_depends_to_service_noargs_returns_none(self, contextData):
        deployment_env = f"./.{contextData['deployment_name']}.env"
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
        "links": module.keycloak_link(contextData),
        "labels": [
            f"traefik.http.routers.jupyterhub.rule=Host(`opal{contextData['dns_base']}`)",
            f"traefik.http.routers.jupyterhub_api.rule=Host(`jupyterhub_api{contextData['mod_base']}`)"
        ]
    }
        arg = []
        actual = module.add_depends_to_service(jupyter_service, arg)
        assert actual == None

    def test_generate_docker_compose(self,contextData):
        expected = {'version': '3.9', 
                    'services': {
                        'postgresql': {'env_file': ['./.test_context.env']}, 
                        'singleuser': {'build': {'context': '.', 'dockerfile': './singleuser/Dockerfile', 'args': {'OPAL_BANNER_COLOR': 'Y', 'OPAL_BANNER_TEXT': 'orange'}}}, 
                        'jupyterhub': {'build': {'args': {'OPAL_BANNER_COLOR': 'Y', 'OPAL_BANNER_TEXT': 'orange'}}, 'volumes': ['./jupyterhub/dev.jupyterhub_config.py:/home/jovyan/jupyterhub_config.py'], 'env_file': ['./.test_context.env'], 'environment': ['OPAL_BANNER_COLOR=Y', "OPAL_BANNER_TEXT='orange'"], 'links': ['traefik:keycloak'], 'labels': ['traefik.http.routers.jupyterhub.rule=Host(`opal`)', 'traefik.http.routers.jupyterhub_api.rule=Host(`jupyterhub_api`)'], 'depends_on': {'keycloak': {'condition': 'service_healthy'}}}, 
                        'traefik': {'volumes': ['./keycloak/certs/test_context:/etc/traefik/certs/'], 'env_file': ['./.test_context.env'], 'depends_on': {'keycloak': {'condition': 'service_healthy'}, 'keycloak_setup': {'condition': 'service_started'}}}, 
                        'keycloak': {'image': '${KEYCLOAK_IMAGE}', 'depends_on': {'postgresql': {'condition': 'service_healthy'}}, 'volumes': ['./keycloak/certs/test_context/tls.key:/etc/x509/https/tls.key', './keycloak/certs/test_context/tls.crt:/etc/x509/https/tls.crt'], 'env_file': ['./.env.secrets', './.test_context.env', './.env'], 'healthcheck': {'test': ['CMD-SHELL', 'curl --fail http://localhost:9990/health'], 'interval': '60s', 'timeout': '5s', 'start_period': '60s', 'retries': 10}, 'labels': ['traefik.enable=true', 'traefik.http.routers.keycloak.rule=Host(`keycloak`)', 'traefik.http.routers.keycloak.entrypoints=websecure', 'traefik.http.services.keycloak.loadbalancer.server.port=8080', 'traefik.http.routers.keycloak.service=keycloak'], 'restart': 'always'}, 
                        'keycloak_setup': {'image': '${KEYCLOAK_IMAGE}', 'depends_on': {'keycloak': {'condition': 'service_healthy'}}, 'env_file': ['./.env.secrets', './.test_context.env', './.env'], 'healthcheck': {'test': ['CMD-SHELL', 'curl --fail http://localhost:9990/health'], 'interval': '60s', 'timeout': '5s', 'start_period': '60s', 'retries': 10}, 'restart': 'no', 'volumes': ['./keycloak/keycloak_script.sh:/usr/local/bin/keycloak_script.sh'], 'entrypoint': ['sh', '/usr/local/bin/keycloak_script.sh']}, 
                        'minio': {'image': '${MINIO_IMAGE}', 'command': 'server --console-address ":9002" --certs-dir /home/minio/certs /home/minio/data{1...4}', 'env_file': ['./.env.secrets', './.test_context.env', './.env'], 'volumes': ['./keycloak/certs/test_context/tls.crt:/home/minio/certs/CAs/tls.crt'], 'links': ['traefik:keycloak'], 'labels': ['traefik.enable=true', 'traefik.http.routers.minio.rule=Host(`minio`)', 'traefik.http.routers.minio.entrypoints=websecure', 'traefik.http.services.minio.loadbalancer.server.port=9002', 'traefik.http.routers.minio.service=minio', 'traefik.http.routers.minio_api.rule=Host(`minio_api`)', 'traefik.http.routers.minio_api.entrypoints=websecure', 'traefik.http.services.minio_api.loadbalancer.server.port=9000', 'traefik.http.routers.minio_api.service=minio'], 'restart': 'always'}}}
        actual = module.generate_docker_compose(contextData)
        assert actual == expected