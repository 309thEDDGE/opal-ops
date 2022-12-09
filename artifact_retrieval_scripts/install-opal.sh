#!/usr/bin/env bash

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

############################################################
#                     Initial Checks                       #
############################################################

# Many parts of this process need to be run with sudo, so we use this to check
# prior to running those. If the user isn't elevated, they will be prompted for their password

_run_as_root() {
  if [[ "$EUID" -ne 0 ]]
  then
    _yellow ". Attempting to run $@ with elevated privileges. You may be prompted for your password"
    sudo bash "$@"
  else
    bash "$@"
    #_green Pass
  fi
}

_yellow "Checking bzip2 is installed"
if [ "$(which bzip2)" == "" ]
then
  _red "Bzip2 is not installed. Please install it and run this script again"
  exit
fi
  

############################################################
#            Check For Expected File Structure             #
############################################################

_expected=("./docker" "./images" "./load-docker-images.sh" "./unpacker.sh")

_blue "Checking for expected files"

# the below supposedly works on bash > 4.4, but I only have zsh on my machines so I can't actually test it
#readarray -d '' array < <(find . -print0)

# We use this instead since it works on zsh
array=()
while IFS= read -r -d ''; do
    array+=("$REPLY")
done < <(find . -print0)

# The below may be useful at some point, but for now the case statement should be enough
#_common=($(comm -12 <(printf "%s\n" "${array[@]}" | LC_ALL=C sort) <(printf "%s\n" "${_expected[@]}" | LC_ALL=C sort)))
#echo "${_common[@]}"

_images_present=0
_unpacker_present=0
_docker_present=0
_image_loader_present=0

# There may be a more elegant solution. This gets the job done though, so :shrug:
for i in "${array[@]}"
do
  case $i in
    "./docker")
      echo -e "\tFound ./docker/"
      _docker_present=1;;
    "./load-docker-images.sh")
      echo -e "\tFound ./load-docker-images.sh"
      _image_loader_present=1;;
    "./images")
      echo -e "\tFound ./images"
      _images_present=1;;
    "./unpacker.sh")
      echo -e "\tFound ./unpacker.sh"
      _unpacker_present=1;;
    *)
  esac
done

echo

############################################################
#              Unpack and Organize Artifacts               #
############################################################

_blue "Prepping to unpack artifacts"

bash unpacker.sh

mv ./images/opal-ops .

echo

############################################################
#                     Install Docker                       #
############################################################

_install_docker() {
  _blue "Prepping to install Docker"
  pushd ./docker
  _run_as_root ./install-docker.sh
  popd
  echo
}

############################################################
#                   Installation Stages                    #
############################################################

#------------------------------------------------------------
#-                 Unpack Images Directory                  -
#------------------------------------------------------------

# This is the big one for the installer. If neither of these files aren't present, halt execution
if [[ $_images_present == 0 || $_unpacker_present == 0 || $_image_loader_present == 0 ]]
then
  _red "Required files missing. Ensure \`unpacker.sh\`, \`load-docker-images\`, and \`images\` are in the same directory as \`install-opal.sh\`"
  exit
fi

#------------------------------------------------------------
#-                     Install Docker                       -
#------------------------------------------------------------

# Optional stage. If these aren't present, we'll assume docker doesn't need to be installed
if [[ $_docker_present == 1 ]]
then
  _blue "Detected Docker binaries"
  _install_docker
else
  _blue "No Docker binaries found. Skipping Docker install"
fi

#------------------------------------------------------------
#-                   Load Docker Images                     -
#------------------------------------------------------------

_blue "Loading Docker images"

_run_as_root load-docker-images.sh

echo

#------------------------------------------------------------
#-                     Configure OPAL                       -
#------------------------------------------------------------

_blue "Beginning OPAL configuration"

pushd opal-ops/docker-compose/configuration

bash new_deployment.bash

popd

echo
