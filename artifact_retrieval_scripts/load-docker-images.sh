#!/bin/bash

set -e

_blue() {
  echo -e "\e[1;36m$@\e[0m"
}
_red() {
  echo -e "\e[1;31m$@\e[0m"
}
_green() {
  echo -e "\e[1;32m$@\n\e[0m"
}
_yellow() {
  echo -e "\e[1;33m$@\e[0m"
}

_check_root_user() {
  if [[ $EUID -ne 0 ]]
  then
    _red "$0 is not running as root. Switch to root user before running script."
    exit 2
  else
    _green Pass
  fi
}

_docker_comp() {
	EXP="$1"
	OBS="$2"
	COMPLETE_EXP=$3
	COMPLETE_OBS=$4

	# If both observed and expected components are empty it's a pass.
	# If observed is empty and expected is not it's a fail. 
	# If observed is not empty and expected is empty it's a pass.
	if [[ -z $OBS ]] 
	then
		if [[ ! -z $EXP ]]
		then 
			_red "Docker version $COMPLETE_OBS < $COMPLETE_EXP"	
			exit 2
		fi
	elif [[ -z $EXP ]]
	then
		return 0
	fi

	if [[ $OBS -lt $EXP ]]
	then
		_red "Docker version $COMPLETE_OBS < $COMPLETE_EXP"	
		exit 2
	fi
	return 0
}

_check_docker_version() {
	OBSERVED_DOCKER_VERSION=$(docker --version | grep -Eo '[0-9]{2}\.[0-9]{1,2}\.[0-9]{1,2}' | head -n 1 2>/dev/null)
	if [[ -z $OBSERVED_DOCKER_VERSION ]]
	then
		_red "\"docker --version\" command failed. Docker must be installed to continue."
		exit 2
	fi

	EXPECTED_DOCKER_VERSION=$1
	EXP_MAJ=$(echo $EXPECTED_DOCKER_VERSION | cut -f1 -d.)
	EXP_MIN=$(echo $EXPECTED_DOCKER_VERSION | cut -f2 -d.)
	EXP_REV=$(echo $EXPECTED_DOCKER_VERSION | cut -f3 -d.)

	OBS_MAJ=$(echo $OBSERVED_DOCKER_VERSION | cut -f1 -d.)
	OBS_MIN=$(echo $OBSERVED_DOCKER_VERSION | cut -f2 -d.)
	OBS_REV=$(echo $OBSERVED_DOCKER_VERSION | cut -f3 -d.)

	_docker_comp "$EXP_MAJ" "$OBS_MAJ" "$EXPECTED_DOCKER_VERSION" "$OBSERVED_DOCKER_VERSION"
	if [[ $OBS_MAJ -gt $EXP_MAJ ]]
	then
		_green Pass
		return 0
	fi

	_docker_comp "$EXP_MIN" "$OBS_MIN" "$EXPECTED_DOCKER_VERSION" "$OBSERVED_DOCKER_VERSION"
	if [[ $OBS_MIN -gt $EXP_MIN ]]
	then
		_green Pass
		return 0
	fi 

	_docker_comp "$EXP_REV" "$OBS_REV" "$EXPECTED_DOCKER_VERSION" "$OBSERVED_DOCKER_VERSION"
	_green Pass
	return 0
}

_load_images() {
	images=$(ls ./images | grep '.tar')
	for image in $images
	do
		_yellow "Loading image $image"
		docker load -i "./images/$image"
	done
	_green Pass
}

_blue Checking user is root 
_check_root_user

_blue Checking docker version
_check_docker_version '19.03' 

_blue Loading images into docker daemon
_load_images

