def format_control_script(context):
    file = f"""#!/bin/bash
_blue() {{
  echo -e $'\e[1;36m'"$@"$'\e[0m'
}}
_red() {{
  echo -e $'\e[1;31m'"$@"$'\e[0m'
}}
_green() {{
  echo -e $'\e[1;32m'"$@"$'\e[0m'
}}
_yellow() {{
  echo -e $'\e[1;33m'"$@"$'\e[0m'
}}

set -e
_green "Checking Docker Compose Version"

if [[ $(docker compose version) == *"version v2."* ]] ; then
    COMPOSE="docker compose"
    _green "using $(docker compose version)"
elif [[ $(docker-compose version) == *"version v2."* ]] ; then
    COMPOSE="docker-compose"
    _green "using $(docker-compose version)"
elif [[ $(docker-compose -v) == *"version 1."* ]] ; then
    _red "Can't use docker compose version 1 from $(docker-compose -v)"
    exit 1
else
  _red "Unable to verify Docker Compose Version check to see if it is running."
  exit 1
fi



generate_manifest(){{
    bash ../deployment-verification/generate_manifest.bash {context['deployment_name']}
}}

start(){{
    FILE=./.env.secrets

    if test -f "$FILE"; then
        _green Found secret file. Deploying
    else
        _red Secrets missing. Please copy the secrets template file and fill out the values
        _yellow The template can be copied like so:
        _yellow cp .env.secrets_template .env.secrets
        exit 1
    fi

    mkdir -p ./jupyter_mounts/metaflow_metadata
    chmod -R 777 ./jupyter_mounts

    generate_manifest
    $COMPOSE -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json build
    $COMPOSE -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json up -d
}}

# Full restart of OPAL to avoid any odd quirks that may be caused by docker compose restart
restart(){{
    _green Restarting OPAL
    generate_manifest
    $COMPOSE -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json down
    $COMPOSE -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json up -d
}}


stop(){{
    _green Shutting down OPAL
    $COMPOSE -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json down
}}

# Display usage options
help(){{
    echo "OPAL Control Utility"
    echo
    echo "Syntax: ./$(basename $0) [ -h | --help | start | stop | restart ]"
    echo "options:"
    echo "-h, --help     : print this help message and exit"
    echo "start          : start OPAL"
    echo "stop           : shutdown OPAL"
    echo "restart        : restart OPAL"
    echo
    exit
}} 


if [ $# -gt 0 ]
then
    case $1 in
        -h | --help)
            help
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        *)
            _yellow "Unrecognized option. Displaying help message."
            echo
            help
            ;;
    esac
else
    help
fi
    """
    return file


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


    print(format_control_script(context_data))

