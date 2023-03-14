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

# #Variable instantiation
# 1=$PWD

#Check for an existing and valid path provided by the user
check_input_is_path(){
    #Check that the user-provided directory exists
    if [ ! -d $1 ]
    then
        _red "Input path is not a directory"
        return 1
    #Check if the user path contains an out.json file
    elif [ ! -f "$1/docker-compose/out.json" ]
    then
        _red "This directory does not appear to have an out.json file from a complete OPAL installation"
        return 1
    fi
    echo
    _green "Destination directory contains a valid opal-ops"
    return 0
}

#Check if a backup directory exists and if not, create one
make_backups_if_not_exists(){
    if [ ! -d "$1/backups" ]
    then
        _blue "A backups directory was not found, creating directory: $1/backups"
        mkdir $1/backups
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
        if [ -f "$1/backups/${todays_date}_v${version}.tar.gz" ]
        then
            ((version++))
        #Search for the highest (single digit) version and increment once
        elif [ -f "$1/backups/${todays_date}_v0${version}.tar.gz" ]
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
            _blue "Creating backup: $1/backups/${todays_date}_v0${version}.tar.gz"
            tar -czf "$1/backups/${todays_date}_v0${version}.tar.gz" "$1/docker-compose" "$1/deployment-verification" >/dev/null 2>&1
    else
            _blue "Creating backup: $1/backups/${todays_date}_v${version}.tar.gz"
            tar -czf "$1/backups/${todays_date}_v${version}.tar.gz" "$1/docker-compose" "$1/deployment-verification" >/dev/null 2>&1
    fi
}

#Overwrite/copy new files to current deployment
overwrite_files(){
    #Identify source and destination locations
    destination=$1
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

init_test_dir(){
    temp_dir=$1

    if [ -d $temp_dir ]
    then
        rm -rf $temp_dir
    fi

    mkdir $temp_dir
    #Array of directories where the above files live
    copied_directories=(
        deployment-verification
        docker-compose
        docker-compose/configuration
        docker-compose/jupyterhub
        docker-compose/keycloak
        docker-compose/minio
        docker-compose/opal
        docker-compose/postgresql
        docker-compose/singleuser
        docker-compose/singleuser_dev
        docker-compose/traefik
        .git
    )

    #Create the directories and structure for files to be copied.
    for dir in ${copied_directories[@]}
    do
        mkdir -p $temp_dir/$dir
    done

    


    cat <<< "{
        "deployment_name": "testOpal",
        "dns_base": ".127.0.0.1.nip.io",
        "mod_base": ".127.0.0.1.nip.io",
        "banner_color": "blue",
        "banner_text": "testing",
        "singleuser_type": "singleuser",
        "deploy_keycloak": true,
        "deploy_minio": true
    }" > $temp_dir/docker-compose/out.json
}

run_diffs(){
    temp_dir=$1
    source=$2
    #Array of static files that were overwritten
    files_to_test=(
        README.md 
        deployment-verification/
        docker-compose/.env
        docker-compose/configuration/
        docker-compose/docker-compose.yml
        docker-compose/jupyterhub/shared_jupyterhub_config.py
        docker-compose/jupyterhub/Dockerfile
        docker-compose/keycloak/keycloak_script.sh
        docker-compose/minio/
        docker-compose/opal/
        docker-compose/postgresql/
        docker-compose/singleuser/
        docker-compose/singleuser_dev/
        docker-compose/traefik/
        .git/)

    diff_failed=0

    #Check for any differences between the source and temporary directory.
    #Report a pass or fail and the differences when applicable.
    for file in ${files_to_test[@]}
    do
        # cp -af $source/$file $destination/temp-copy-directory/$file
        DIFF=$(diff -r $source/$file $temp_dir/$file)
        if [ "$DIFF" != "" ]
        then
            echo "$file: FAIL"
            #echo $DIFF
            diff_failed=1
        else
            echo "$file: PASS"
        fi
    done

    return $diff_failed
}

print_expected_pass(){
    status=$1

    if [ $status -eq 1 ]
    then
        _red "Test: FAIL"
    else
        _green "Test: PASS"
    fi
}

print_expected_fail(){
    status=$1

    if [ $status -eq 0 ]
    then
        _red "Test: FAIL"
    else
        _green "Test: PASS"
    fi
}

cleanup_dir(){
    if [ -d $1 ]
    then
        rm -rf $1
    fi
}

#Test the overwrite_files function to ensure everything copied and overwrote correctly.
#IMPORTANT: Be sure to have deepdiff installed locally to run this. Use "pip install deepdiff"
run_tests(){
    #Make a temporary directory to test the copy
    temp_dir=$PWD/temp-copy-directory

    source=$PWD
    
    #echo $temp_dir
    #echo $PWD
    init_test_dir $temp_dir

    #Copy files to the temporary directory to confirm functionality
    # for file in ${files_to_test[@]}
    # do
    #     #cp -af $source/$file $destination/$temp_dir/$file
    echo ==================================================================================
    _blue "                               Testing copy"
    echo ==================================================================================
    overwrite_files $temp_dir 
    run_diffs $temp_dir $source
    print_expected_pass $?

    echo ==================================================================================
    _blue "                    Testing changes to intentionally fail"
    echo ==================================================================================
    init_test_dir $temp_dir
    overwrite_files $temp_dir 
    echo "Changed the README" > $temp_dir/README.md
    run_diffs $temp_dir $source
    print_expected_fail $?


    echo ==================================================================================
    _blue "          Testing check_input_is_path fails on missing out.json"
    echo ==================================================================================
    init_test_dir $temp_dir
    rm $temp_dir/docker-compose/out.json
    check_input_is_path $temp_dir
    print_expected_fail $?


    echo ==================================================================================
    _blue "          Testing check_input_is_path fails on missing directory"
    echo ==================================================================================
    init_test_dir $temp_dir
    rm -rf $temp_dir
    check_input_is_path $temp_dir
    print_expected_fail $?


    echo ==================================================================================
    _blue "          Testing check_input_is_path passes with correct filestructure"
    echo ==================================================================================
    init_test_dir $temp_dir
    check_input_is_path $temp_dir
    print_expected_pass $?
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
    _green "====================================="
    _green "          OPAL Update Tool       "
    _green "====================================="
    check_input_is_path "$1"
    if [ $? -eq 1 ]
    then
        exit 1
    fi
    make_backups_if_not_exists "$1"
    make_date_backup_dir "$1"
    overwrite_files "$1"
}

#Check for proper usage from user
if [ $# -gt 0 ]
then
    case $1 in
        -h | --help)
            help
            ;;
        -t | --test)
            run_tests
            ;;
        *)
            main "$1"
            ;;
    esac
else
    help
fi