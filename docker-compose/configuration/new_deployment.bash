#!/bin/bash


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

#call python cmd
python --version 2&> /dev/null

#check python version is 0, if not then script will exit
if [[ $? -eq 0 ]]; then 
  python2 --version 2&> /dev/null
  if [[ $? -eq 0 ]]; then
    _red "This script requires python 3.0 or greater"
    _yellow "checking python3"
    python3 --version 3&> /dev/null
    if [[ $? -eq 0 ]]; then
      _green "python 3 found!"
      PYTHON=python3
    else
      echo "Please update your Python to version 3.0 or greater"
      exit 1
    fi
  fi
else
  exit 1
fi

#assign python variables 


echo "$ver3"

#set the python alias
PYTHON=python

#check the version of python with "python" alias.  If its less than 3 than check python3 alias and assign.


# change working directory to docker-compose
cd "$(dirname $0)/.."

# ask the user some questions
_green "====================================="
_green "       OPAL Configuration Tool       "
_green "====================================="
$PYTHON configuration/make_context.py out.json

# get the deployment name from out.json
# jq might not be insalled on the system, so it's sed time
DEPLOYMENT_NAME=$(grep -r '"deployment_name\": "[^"]*"' out.json | sed 's/.*://g;s/[\ ",]//g')

_green "-------------------------------------"
_green "    Generating files for $DEPLOYMENT_NAME"
_green "-------------------------------------"

# generate files
_blue " - Generating $DEPLOYMENT_NAME.docker-compose.json"
$PYTHON configuration/generate_docker_compose.py out.json > $DEPLOYMENT_NAME.docker-compose.json
_blue " - Generating .$DEPLOYMENT_NAME.env"
$PYTHON configuration/generate_env.py out.json > .$DEPLOYMENT_NAME.env
_blue " - Generating $DEPLOYMENT_NAME""_util.sh"
$PYTHON configuration/generate_opal_control_script.py out.json > $DEPLOYMENT_NAME\_util.sh
chmod +x $DEPLOYMENT_NAME\_util.sh
_blue " - Generating OPAL_$DEPLOYMENT_NAME.service"
_yellow "\t- Copy OPAL_$DEPLOYMENT_NAME.service to /etc/systemd/system/ and run:"
_yellow "\t- 'systemctl daemon-reload && systemctl enable OPAL_$DEPLOYMENT_NAME.service'"
_yellow "\t- to automatically start OPAL on system reboot"
$PYTHON configuration/generate_service_file.py out.json > OPAL_$DEPLOYMENT_NAME.service

# generate secrets if necessary
if test -f .env.secrets; then
    _blue " - Found secrets file .env.secrets"
    _yellow "\t- No secrets file will be generated"
else
    _blue " - No secrets file found - generating .env.secrets"
    $PYTHON configuration/generate_secrets.py > ./.env.secrets
fi

_green "-------------------------------------"
_green "       Configuration Complete        "
_green "-------------------------------------"

_blue "Run"
_blue "\t$DEPLOYMENT_NAME""_util.sh start"
_blue "to start OPAL"
