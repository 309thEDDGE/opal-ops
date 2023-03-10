#!/bin/bash

#define color-coding
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

#Variable instantiation
CWD=$PWD

#Check for an existing and valid path provided by the user
check_input_is_path(){
    _green "====================================="
    _green "          OPAL Update Tool       "
    _green "====================================="

    #Check that the user-provided directory exists
    if [ ! -d $1 ]
    then
        _red "Input path is not a directory"
        exit 1
    #Check if the user path contains an out.json file
    elif [ ! -f "$1/docker-compose/out.json" ]
    then
        _red "This directory does not appear to have an out.json file from a complete OPAL installation"
        exit 1
    fi
    echo
    _green "Destination directory contains a valid opal-ops"
    CWD=$1
}

#Check if a backup directory exists and if not, create one
make_backups_if_not_exists(){
    if [ ! -d "$CWD/backups" ]
    then
        _blue "A backups directory was not found, creating directory: $CWD/backups"
        mkdir $CWD/backups
    fi
}

#Create a directory with todays date and version number inside backups
make_date_backup_dir(){
    todays_date="$(date +"%Y.%m.%d")"
    version=1
    looping=0
    #Loop through the backups directory for existing versions
    while [ $looping -eq 0 ]
    do
        #Search for the highest (double digit) version already created and increment once
        if [ -f "$CWD/backups/${todays_date}_v${version}.tar.gz" ]
        then
            ((version++))
        #Search for the highest (single digit) version and increment once
        elif [ -f "$CWD/backups/${todays_date}_v0${version}.tar.gz" ]
        then
            ((version++))
        else
            looping=1
        fi
    done

    #Add a zero in front of single digits to display better from the terminal,
    #create the directory with correct version, and compress the copied backups
    if [[ $version -lt 10 ]]
    then
            _blue "Creating backup: $CWD/backups/${todays_date}_v0${version}.tar.gz"
            tar -czf "$CWD/backups/${todays_date}_v0${version}.tar.gz" "$CWD/docker-compose" "$CWD/deployment-verification" >/dev/null 2>&1
    else
            _blue "Creating backup: $CWD/backups/${todays_date}_v${version}.tar.gz"
            tar -czf "$CWD/backups/${todays_date}_v${version}.tar.gz" "$CWD/docker-compose" "$CWD/deployment-verification" >/dev/null 2>&1
    fi
}

#Overwrite/copy new files to current deployment
overwrite_files(){
    #Identify source and destination locations
    destination=$CWD
    echo
    echo "Destination   : " $destination
    source=$PWD
    echo "Source        : " $source
    echo

    #Copy README
    echo "Copying README to $destination"
    cp -af $source/README.md $destination

    #Copy deployment-verification scripts
    echo "Copying Deployment-Verification to $destination"
    cp -af $source/deployment-verification $destination

    #Copy docker-compose directories/files
    #blindly copying all files risks overwriting of local customizations
    echo "Copying Docker-Compose to $destination"
    cp -af $source/docker-compose/.env $destination/docker-compose
    cp -af $source/docker-compose/configuration $destination/docker-compose
    cp -af $source/docker-compose/docker-compose.yml $destination/docker-compose
    cp -af $source/docker-compose/jupyterhub/shared_jupyterhub_config.py $destination/docker-compose/jupyterhub
    cp -af $source/docker-compose/jupyterhub/Dockerfile $destination/docker-compose/jupyterhub
    cp -af $source/docker-compose/keycloak/keycloak_script.sh $destination/docker-compose/keycloak
    cp -af $source/docker-compose/minio $destination/docker-compose
    cp -af $source/docker-compose/opal $destination/docker-compose
    cp -af $source/docker-compose/postgresql $destination/docker-compose
    cp -af $source/docker-compose/singleuser $destination/docker-compose
    cp -af $source/docker-compose/singleuser_dev $destination/docker-compose
    cp -af $source/docker-compose/traefik $destination/docker-compose
    
    #Copy .git directory
    echo "Copying .git"
    cp -af $source/.git $destination
}

#Test the overwrite_files function to ensure everything copied and overwrote correctly
test_overwrite_files(){
    _green "====================================="
    _green "       Testing Overwrite Files       "
    _green "====================================="

    #Create differing test files to test diff
    echo "Source Test File" > $source/test-file-SHOULD-FAIL.txt
    echo "Destination Test File" > $destination/test-file-SHOULD-FAIL.txt

    #Array of static files that were overwritten
    files_to_test=(
        test-file-SHOULD-FAIL.txt
        README.md 
        deployment-verification
        docker-compose/.env
        docker-compose/configuration
        docker-compose/docker-compose.yml
        docker-compose/jupyterhub/shared_jupyterhub_config.py
        docker-compose/jupyterhub/Dockerfile
        docker-compose/keycloak/keycloak_script.sh
        docker-compose/minio
        docker-compose/opal
        docker-compose/postgresql
        docker-compose/singleuser
        docker-compose/singleuser_dev
        docker-compose/traefik
        .git)

    #Check for any differences between the source and location files.
    #Report a pass or fail and the differences when applicable.
    for file in ${files_to_test[@]}
    do
        DIFF=$(diff -r $source/$file $destination/$file)
        if [ "$DIFF" != "" ]
        then
            _red "$file: FAIL"
            echo $DIFF
        else
            _green "$file: PASS"
        fi
    done

    #Remove the test files from both locations
    rm $source/test-file-SHOULD-FAIL.txt
    rm $destination/test-file-SHOULD-FAIL.txt
}


# Display usage options
help(){
    echo "OPAL Update Utility"
    echo
    echo "Syntax: ./$(basename $0) [ -h | --help | /path/to/current/opal-ops/ ]"
    echo "options:"
    echo "-h, --help              : Print this help message and exit"
    echo "/path/to/current/opal-ops/  : Current opal-ops configuration directory"
    echo
    exit
}

#Driver for all functions
main(){
    check_input_is_path "$1"
    make_backups_if_not_exists
    make_date_backup_dir
    overwrite_files
    test_overwrite_files #Comment out when not needing built-in-test
}

#Check for proper usage from user
if [ $# -gt 0 ]
then
    case $1 in
        -h | --help)
            help
            ;;
        *)
            main "$1"
            ;;
    esac
else
    help
fi