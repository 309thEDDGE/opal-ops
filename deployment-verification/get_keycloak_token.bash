
URL="$1/auth/realms/master/protocol/openid-connect/token"
RES=$(curl --location --insecure -s --request POST $URL \
     --header 'Content-Type: application/x-www-form-urlencoded' \
     --data-urlencode 'client_id=admin-cli' \
     --data-urlencode "username=$2" \
     --data-urlencode "password=$3" \
     --data-urlencode 'grant_type=password')

if [[ $RES == *"\"access_token\":"* ]]; then
	if [[ $* == *" --raw" ]]; then
		echo $RES
	else
		echo $(echo $RES | jq .access_token | sed -e 's/"//g')
	fi
	exit 0
else
	echo $RES
	exit 1
fi
