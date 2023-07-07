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
#checking python version

read -r -d '' ISPYTHON3 <<-'EOF'
	import platform
	import sys
	major = platform.python_version_tuple()[0]
	sys.exit(0 if int(major) >= 3 else 1)
EOF

get_python_3() {
	for py in $@ ; do
		if $py -c "$ISPYTHON3" &>/dev/null ; then
			echo "$py"
			return
		fi
	done
}

PYTHON3=$(get_python_3 $PYTHON3 $PYTHON $(which python) $(which python3))
if [[ -z "${PYTHON3}" ]] ; then
	echo "no python3 found"
	exit 1
elif ! "${PYTHON3}" --version &>/dev/null ; then
	echo "bad python3"
	exit 1
fi

#echo "using PYTHON3 ${PYTHON3}"

# Test if read bit is set for other users
_is_readable() {
  if [[ ! -f "$1" ]]; then
      _red "Testing if $1 has read bit but it doesn't exist!"
      exit 1
  fi
  permissions=$(stat -c "%a" "$1")
  permissions=${permissions: -1: 1}
  if [[ $(( $permissions & 100)) -eq 0 ]]; then
      _red "Read bit not set for other users: $1"
      exit 1
  fi
}
_is_readable "../postgresql/postgres-bootstrap.sql"


# change working directory to docker-compose
cd "$(dirname $0)/.."

# ask the user some questions
_green "====================================="
_green "       OPAL Configuration Tool       "
_green "====================================="



if [[ $# -eq 0 ]]; then
  $PYTHON3 configuration/make_context.py out.json
  CONTEXT_FILE=out.json
else
  CONTEXT_FILE=$1
  $PYTHON3 configuration/generate_files/validate_out_json.py $CONTEXT_FILE
fi


# get the deployment name from out.json
# jq might not be insalled on the system, so it's sed time
DEPLOYMENT_NAME=$(grep -r '"deployment_name\": "[^"]*"' $CONTEXT_FILE | sed 's/.*://g;s/[\ ",]//g')

_green "-------------------------------------"
_green "    Generating files for $DEPLOYMENT_NAME"
_green "-------------------------------------"

# generate files
_blue " - Generating $DEPLOYMENT_NAME.docker-compose.json"
$PYTHON3 configuration/generate_docker_compose.py $CONTEXT_FILE > $DEPLOYMENT_NAME.docker-compose.json
_blue " - Generating .$DEPLOYMENT_NAME.env"
$PYTHON3 configuration/generate_env.py $CONTEXT_FILE > .$DEPLOYMENT_NAME.env
_blue " - Generating $DEPLOYMENT_NAME""_util.sh"
$PYTHON3 configuration/generate_opal_control_script.py $CONTEXT_FILE > $DEPLOYMENT_NAME\_util.sh

chmod +x $DEPLOYMENT_NAME\_util.sh
_blue " - Generating OPAL_$DEPLOYMENT_NAME.service"
_yellow "\t- Copy OPAL_$DEPLOYMENT_NAME.service to /etc/systemd/system/ and run:"
_yellow "\t- 'systemctl daemon-reload && systemctl enable OPAL_$DEPLOYMENT_NAME.service'"
_yellow "\t- to automatically start OPAL on system reboot"

$PYTHON3 configuration/generate_service_file.py $CONTEXT_FILE > OPAL_$DEPLOYMENT_NAME.service

# generate secrets if necessary
if test -f .env.secrets; then
    _blue " - Found secrets file .env.secrets"
    _yellow "\t- No secrets file will be generated"
else
    _blue " - No secrets file found - generating .env.secrets"
    $PYTHON3 configuration/generate_secrets.py $CONTEXT_FILE > ./.env.secrets
fi

_green "-------------------------------------"
_green "       Configuration Complete        "
_green "-------------------------------------"

_blue "Run"
_blue "\t$DEPLOYMENT_NAME""_util.sh start"
_blue "to start OPAL"
