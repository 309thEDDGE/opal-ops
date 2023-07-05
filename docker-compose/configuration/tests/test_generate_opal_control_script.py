from importer import dynamic_module_import
module = dynamic_module_import('generate_opal_control_script')
import json
import pytest

class TestGenerateOpalControlScript():

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
            "external_minio_url": "external/minio_url",
            "external_keycloak_url": "https://externalURL"
        }"""
        context_json = json.loads(context)
        return context_json

    def test_format_restart_script(self,contextData):
        expected = '#!/bin/bash\n\nset -e\n\nif [[ $(docker compose version) == *"version v2."* ]] ; then\n    COMPOSE="docker compose"\n    echo "using $(docker compose version)"\nelif [[ $(docker-compose version) == *"version v2."* ]] ; then\n    COMPOSE="docker-compose"\n    echo "using $(docker-compose version)"\nelif [[ $(docker-compose -v) == *"version 1."* ]] ; then\n    echo "Can\'t use docker compose version 1 from $(docker-compose -v)"\n    exit 1\nfi\n\n_blue() {\n  echo -e $\'\\e[1;36m\'"$@"$\'\\e[0m\'\n}\n_red() {\n  echo -e $\'\\e[1;31m\'"$@"$\'\\e[0m\'\n}\n_green() {\n  echo -e $\'\\e[1;32m\'"$@"$\'\\e[0m\'\n}\n_yellow() {\n  echo -e $\'\\e[1;33m\'"$@"$\'\\e[0m\'\n}\n\ngenerate_manifest(){\n    bash ../deployment-verification/generate_manifest.bash test_context\n}\n\nstart(){\n    FILE=./.env.secrets\n\n    if test -f "$FILE"; then\n        _green Found secret file. Deploying\n    else\n        _red Secrets missing. Please copy the secrets template file and fill out the values\n        _yellow The template can be copied like so:\n        _yellow cp .env.secrets_template .env.secrets\n        exit 1\n    fi\n\n    mkdir -p ./jupyter_mounts/metaflow_metadata\n    chmod -R 777 ./jupyter_mounts\n\n    generate_manifest\n    $COMPOSE -f docker-compose.yml -f test_context.docker-compose.json build\n    $COMPOSE -f docker-compose.yml -f test_context.docker-compose.json up -d\n}\n\n# Full restart of OPAL to avoid any odd quirks that may be caused by docker compose restart\nrestart(){\n    _green Restarting OPAL\n    generate_manifest\n    $COMPOSE -f docker-compose.yml -f test_context.docker-compose.json down\n    $COMPOSE -f docker-compose.yml -f test_context.docker-compose.json up -d\n}\n\n\nstop(){\n    _green Shutting down OPAL\n    $COMPOSE -f docker-compose.yml -f test_context.docker-compose.json down\n}\n\n# Display usage options\nhelp(){\n    echo "OPAL Control Utility"\n    echo\n    echo "Syntax: ./$(basename $0) [ -h | --help | start | stop | restart ]"\n    echo "options:"\n    echo "-h, --help     : print this help message and exit"\n    echo "start          : start OPAL"\n    echo "stop           : shutdown OPAL"\n    echo "restart        : restart OPAL"\n    echo\n    exit\n} \n\n\nif [ $# -gt 0 ]\nthen\n    case $1 in\n        -h | --help)\n            help\n            ;;\n        start)\n            start\n            ;;\n        stop)\n            stop\n            ;;\n        restart)\n            restart\n            ;;\n        *)\n            _yellow "Unrecognized option. Displaying help message."\n            echo\n            help\n            ;;\n    esac\nelse\n    help\nfi\n    '
        actual = module.format_control_script(contextData)
        assert actual == expected