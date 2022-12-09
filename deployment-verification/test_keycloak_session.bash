#!/bin/bash

if [[ $# < 3 ]]; then
	echo "Usage: test_keycloak_session.bash [keycloak_domain_name] [username] [password]"
	exit 1
fi

echo "Requesting token from $1"
RESPONSE=$(bash get_keycloak_token.bash $1 $2 $3 --raw)
RESPONSE_CODE=$?

echo "--- RAW OUTPUT ---"
echo $RESPONSE
echo "--- RAW OUTPUT ---\n"

ACTION="Retrieve a session token from Keycloak"
REASON="Keycloak tokens are necessary for connecting to other opal services"
if [[ $RESPONSE == *"\"access_token\":"* ]]; then
	echo "Got a token while testing \"$ACTION\" - This is good because $REASON"
elif [[ $RESPONSE == *"error"* ]]; then
	echo "Got an error while testing \"$ACTION\" - This is bad because $REASON"
	echo "This is probably a problem internal to keycloak, or you mistyped your credentials"
	exit 1
else
	echo "Got no response while testing \"$ACTION\" - This is bad because $REASON"
	echo "Keycloak may not be running, or could not be found at $1"
	exit 1
fi
