#!/bin/bash

set -e

_blue() {
  echo -e $'\e[1;36m'"$@"$'\e[0m'
}
_red() {
  echo -e $'\e[1;31m'"$@"$'\e[0m'
}
_green() {
  echo -e $'\e[1;32m'"$@"$'\e[0m'
}
_yellow() {
  echo -e $'\e[1;33m'"$@"$'\e[0m'
}


start(){
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
    chmod 777 -R ./jupyter_mounts

    docker-compose -f docker-compose.yml -f test_context.docker-compose.json build
    docker-compose -f docker-compose.yml -f test_context.docker-compose.json up -d
}

# Full restart of OPAL to avoid any odd quirks that may be caused by docker-compose restart
restart(){
    _green Restarting OPAL
    docker-compose -f docker-compose.yml -f test_context.docker-compose.json down
    docker-compose -f docker-compose.yml -f test_context.docker-compose.json up -d
}


stop(){
    _green Shutting down OPAL
    docker-compose -f docker-compose.yml -f test_context.docker-compose.json down
}

# Display usage options
help(){
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
}


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

