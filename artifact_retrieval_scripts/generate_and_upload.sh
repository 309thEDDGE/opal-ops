#!/usr/bin/env bash

GIT_TAG="$(git tag -l --sort=refname | tail -n 1)"
#GIT_TAG="1234.12.12"
MAX_FILESIZE=4

#git checkout master

echo "If you haven't already logged into the following registries:"
echo "       registry1 (registry1.dso.mil)"
echo "       registry.il2 (registry.il2.dso.mil),"
echo
echo "   please press (ctrl+c) and do so now."

echo "Enter the release tag you would like to download:"

INPUT_VALID=0

read tag

while [ $INPUT_VALID != 1 ]; do
    if [[ "$tag" =~ ^[0-9]{4}\.(0[1-9]|1[0-2])\.(0[1-9]|[1-2][0-9]|3[0-1])$ ]]; then
        echo "Valid date entered, checking out requested tag"
        INPUT_VALID=1
        GIT_TAG=$tag
    elif [[ "$tag" == '' ]]; then
        echo "Defaulting to latest tag"
        INPUT_VALID=1
    else
        echo "That doesn't quite look like a date tag, try again"
        read tag
    fi
done

echo "Maximum filesize in GB:"
echo "(leave empty for 4G)"
echo "(input will be rounded down)"
INPUT_VALID=0
read f_size
while [ $INPUT_VALID != 1 ]; do
    if [[ $f_size =~ ^[0-9] ]]; then
        echo "Valid size entered"
        INPUT_VALID=1
        MAX_FILESIZE = $f_size
    elif [[ "$f_size" == '' ]]; then
        echo "Defaulting to 4GB"
        INPUT_VALID=1
    else
        echo "That input doesn't look valid, try again"
        read f_size
    fi
done

git checkout $GIT_TAG
echo "Generating artifacts with requested tag"

python3 ./release_s3_uploader.py $GIT_TAG $MAX_FILESIZE
