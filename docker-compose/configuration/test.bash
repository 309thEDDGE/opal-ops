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

echo "using PYTHON3 ${PYTHON3}"

# change working directory to docker-compose
cd "$(dirname $0)"

RET=0

##### ORIGINAL TESTS #####

# make the context 
cat test_resources/test_answers/test_answers.txt | $PYTHON3 make_context.py test_resources/test_context_files/actual/test_context_actual.json > /dev/null

PYRET=$?

DIFFS=$(deep diff test_resources/test_context_files/actual/test_context_actual.json test_resources/test_context_files/expected/test_context_expected.json)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR make_context.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS make_context.py"
else
    _red "FAIL make_context.py"
    _yellow $DIFFS
    RET=1
fi

# make the docker-compose
$PYTHON3 generate_docker_compose.py test_resources/test_context_files/expected/test_context_expected.json > test_resources/test_compose_files/actual/test_actual.docker-compose.json

PYRET=$?

DIFFS=$(deep diff test_resources/test_compose_files/expected/test_expected.docker-compose.json test_resources/test_compose_files/actual/test_actual.docker-compose.json)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_docker_compose.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS generate_docker_compose.py"
else
    _red "FAIL generate_docker_compose.py"
    _yellow $DIFFS
    RET=1
fi

# make the environment
$PYTHON3 generate_env.py test_resources/test_context_files/expected/test_context_expected.json > test_resources/test_environment_files/actual/test_actual.env

PYRET=$?

# custom diff test in compare_env.py
DIFFS=$($PYTHON3 test_resources/compare_env.py test_resources/test_environment_files/expected/test_expected.env test_resources/test_environment_files/actual/test_actual.env)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_env.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS generate_env.py"
else
    _red "FAIL generate_env.py"
    _yellow $DIFFS
    RET=1
fi

##### TEST WITH LIGHTWEIGHT SINGLEUSER #####

echo '##### TEST WITH LIGHTWEIGHT SINGLEUSER #####'

# make the context 
cat test_resources/test_answers/test_answers_lightweight.txt | $PYTHON3 make_context.py test_resources/test_context_files/actual/test_context_lightweight_actual.json > /dev/null

PYRET=$?

DIFFS=$(deep diff test_resources/test_context_files/actual/test_context_lightweight_actual.json test_resources/test_context_files/expected/test_context_lightweight_expected.json)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR make_context.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS make_context.py"
else
    _red "FAIL make_context.py"
    _yellow $DIFFS
    RET=1
fi

# make the docker-compose
$PYTHON3 generate_docker_compose.py test_resources/test_context_files/expected/test_context_lightweight_expected.json > test_resources/test_compose_files/actual/test_actual_lightweight.docker-compose.json

PYRET=$?

DIFFS=$(deep diff test_resources/test_compose_files/expected/test_expected_lightweight.docker-compose.json test_resources/test_compose_files/actual/test_actual_lightweight.docker-compose.json)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_docker_compose.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS generate_docker_compose.py"
else
    _red "FAIL generate_docker_compose.py"
    _yellow $DIFFS
    RET=1
fi

# make the environment
$PYTHON3 generate_env.py test_resources/test_context_files/expected/test_context_lightweight_expected.json > test_resources/test_environment_files/actual/test_actual_lightweight.env

PYRET=$?

# custom diff test in compare_env.py
DIFFS=$($PYTHON3 test_resources/compare_env.py test_resources/test_environment_files/expected/test_expected_lightweight.env test_resources/test_environment_files/actual/test_actual_lightweight.env)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_env.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS generate_env.py"
else
    _red "FAIL generate_env.py"
    _yellow $DIFFS
    RET=1
fi

##### TEST WITH LOCALHOST #####

echo '##### TEST WITH LOCALHOST #####'

# make the context 
cat test_resources/test_answers/test_answers_localhost.txt | $PYTHON3 make_context.py test_resources/test_context_files/actual/test_context_localhost_actual.json > /dev/null

PYRET=$?

DIFFS=$(deep diff test_resources/test_context_files/actual/test_context_localhost_actual.json test_resources/test_context_files/expected/test_context_localhost_expected.json)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR make_context.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS make_context.py"
else
    _red "FAIL make_context.py"
    _yellow $DIFFS
    RET=1
fi

# make the docker-compose
$PYTHON3 generate_docker_compose.py test_resources/test_context_files/expected/test_context_localhost_expected.json > test_resources/test_compose_files/actual/test_actual_localhost.docker-compose.json

PYRET=$?

DIFFS=$(deep diff test_resources/test_compose_files/expected/test_expected_localhost.docker-compose.json test_resources/test_compose_files/actual/test_actual_localhost.docker-compose.json)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_docker_compose.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS generate_docker_compose.py"
else
    _red "FAIL generate_docker_compose.py"
    _yellow $DIFFS
    RET=1
fi

# make the environment
$PYTHON3 generate_env.py test_resources/test_context_files/expected/test_context_localhost_expected.json > test_resources/test_environment_files/actual/test_actual_localhost.env

PYRET=$?

# custom diff test in compare_env.py
DIFFS=$($PYTHON3 test_resources/compare_env.py test_resources/test_environment_files/expected/test_expected_localhost.env test_resources/test_environment_files/actual/test_actual_localhost.env)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_env.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS generate_env.py"
else
    _red "FAIL generate_env.py"
    _yellow $DIFFS
    RET=1
fi

##### TEST WITH MODIFIED DNS #####

echo '##### TEST WITH MODIFIED DNS #####'

# make the context 
cat test_resources/test_answers/test_answers_modified_dns.txt | $PYTHON3 make_context.py test_resources/test_context_files/actual/test_context_modified_dns_actual.json > /dev/null

PYRET=$?

DIFFS=$(deep diff test_resources/test_context_files/actual/test_context_modified_dns_actual.json test_resources/test_context_files/expected/test_context_modified_dns_expected.json)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR make_context.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS make_context.py"
else
    _red "FAIL make_context.py"
    _red $DIFFS
    RET=1
fi

# make the docker-compose
$PYTHON3 generate_docker_compose.py test_resources/test_context_files/expected/test_context_modified_dns_expected.json > test_resources/test_compose_files/actual/test_actual_modified_dns.docker-compose.json

PYRET=$?

DIFFS=$(deep diff test_resources/test_compose_files/expected/test_expected_modified_dns.docker-compose.json test_resources/test_compose_files/actual/test_actual_modified_dns.docker-compose.json)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_docker_compose.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS generate_docker_compose.py"
else
    _red "FAIL generate_docker_compose.py"
    _yellow $DIFFS
    RET=1
fi

# make the environment
$PYTHON3 generate_env.py test_resources/test_context_files/expected/test_context_modified_dns_expected.json > test_resources/test_environment_files/actual/test_actual_modified_dns.env

PYRET=$?

# custom diff test in compare_env.py
DIFFS=$($PYTHON3 test_resources/compare_env.py test_resources/test_environment_files/expected/test_expected_modified_dns.env test_resources/test_environment_files/actual/test_actual_modified_dns.env)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_env.py"
    exit 1
elif [[ $DIFFS == "{}" ]]; then
    _green "PASS generate_env.py"
else
    _red "FAIL generate_env.py"
    _yellow $DIFFS
    RET=1
fi


##### TESTING OUTPUT SCRIPTS #####

echo '##### TESTING OUTPUT SCRIPTS #####'


# utility script

$PYTHON3 generate_opal_control_script.py test_resources/test_context_files/expected/test_context_expected.json > test_resources/test_output_scripts/actual/control_script_actual.sh

PYRET=$?

DIFFS=$(diff -w -a test_resources/test_output_scripts/expected/control_script_expected.sh test_resources/test_output_scripts/actual/control_script_actual.sh)

if [[ $PYRET -ne 0 ]]; then
    _red "ERROR generate_opal_control_script.py"
    exit 1
elif [[ ${#DIFFS} == 0 ]]; then
    _green "PASS generate_opal_control_script.py"
else
    _red "FAIL generate_opal_control_script.py"
    echo $DIFFS
    RET=1
fi
