#!/bin/bash

# The following pages will help if this script needs updating:
# https://github.com/keycloak/keycloak-documentation/blob/main/server_admin/topics/admin-cli.adoc
# https://www.keycloak.org/docs-api/15.0/rest-api/index.html

cd /opt/keycloak/bin/

if [[ -z "${EXTERNAL_KEYCLOAK}" ]]; then
    EXTERNAL_KEYCLOAK=http://keycloak:8080/
fi

authenticate_keycloak () {
./kcadm.sh config credentials \
            --server $EXTERNAL_KEYCLOAK/auth \
            --user $KEYCLOAK_ADMIN \
            --password $KEYCLOAK_ADMIN_PASSWORD \
            --realm master
}

until authenticate_keycloak; do
    if [ $? -eq 1 ]; then
        echo "keycloak_setup cannot authenticate. It is likely the keycloak server is still booting. Retrying in 2 seconds"
	sleep 2
    else
        echo "keycloak_setup successfully authenticated"
    fi
done

echo "Bootstrapping Keycloak config"

# Don't require ssl
echo "Disabling ssl"
./kcadm.sh update realms/master -s sslRequired=NONE

# Jupyterhub client creation
echo "Creating opal-jupyterhub client"
JUPYTERHUB_CLIENT_ID=$(./kcadm.sh create clients \
            --server $EXTERNAL_KEYCLOAK/auth \
            -r master \
            -s clientId=$KEYCLOAK_JUPYTERHUB_CLIENT_ID \
            -s 'redirectUris=["*"]' \
	        -s 'attributes."access.token.lifespan"=60480000' \
            -s secret=$KEYCLOAK_JUPYTERHUB_CLIENT_SECRET -i)

echo "Creating jhub-group-mapper in opal-jupyterhub client with $JUPYTERHUB_CLIENT_ID"
./kcadm.sh create clients/$JUPYTERHUB_CLIENT_ID/protocol-mappers/models \
            -r master \
            -s name=jhub-group-mapper \
            -s protocol=openid-connect \
            -s protocolMapper=oidc-group-membership-mapper \
            -s 'config."full.path"=false' \
            -s 'config."id.token.claim"=true' \
	        -s 'config."access.token.claim"=true' \
            -s 'config."claim.name"=groups' \
            -s 'config."userinfo.token.claim"=true'

# Minio client creation

# Minio client mapper creation
echo "Creating miniopolicyclaim mapper for opal-jupyterhub client with $JUPYTERHUB_CLIENT_ID"
./kcadm.sh create clients/$JUPYTERHUB_CLIENT_ID/protocol-mappers/models \
            -r master \
            -s name=miniopolicyclaim \
            -s protocol=openid-connect \
            -s protocolMapper=oidc-usermodel-attribute-mapper \
            -s 'config."id.token.claim"=true' \
            -s 'config."userinfo.token.claim"=true' \
            -s 'config."user.attribute"=policy' \
            -s 'config."id.token.claim"=true' \
            -s 'config."access.token.claim"=true' \
            -s 'config."claim.name"=policy' \
            -s 'config."jsonType.label"=String'


# Enable event logging for the master realm. Events expire after 14 days
./kcadm.sh update events/config -r master -s eventsEnabled=true -s 'enabledEventTypes=[]' -s eventsExpiration=1209600



# This is for creating a Minio client. Currently minio and jupyterhub share a client
# MINIO_CLIENT_ID=$(./kcadm.sh create clients \
#             --server http://keycloak:8080/auth \
#             -r master \
#             -s clientId=$MINIO_IDENTITY_OPENID_CLIENT_ID \
#             -s 'redirectUris=["*"]' \
#             -s secret=$KEYCLOAK_MINIO_CLIENT_SECRET \
#             -s directAccessGrantsEnabled=true -i)


# -s 'redirectUris=["$MINIO_IDENTITY_OPENID_REDIRECT_URI"]' \
    # Minio client mapper creation
# echo $MINIO_IDENTITY_OPENID_CLAIM_NAME
# ./kcadm.sh create clients/$MINIO_CLIENT_ID/protocol-mappers/models \
#             -r master \
#             -s name=$MINIO_CLIENT_ID \
#             -s protocol=openid-connect \
#             -s protocolMapper=oidc-usermodel-attribute-mapper \
#             -s 'config."id.token.claim"=true' \
#             -s 'config."userinfo.token.claim"=true' \
#             -s 'config."user.attribute"=policy' \
#             -s 'config."id.token.claim"=true' \
#             -s 'config."access.token.claim"=true' \
#             -s 'config."claim.name"=policy' \
#             -s 'config."jsonType.label"=String'

# Minio Admin user creation
echo "creating minio test user"
./kcadm.sh create users \
            -r master\
            -s username=$MINIO_TEST_USER \
            -s "attributes.policy=consoleAdmin"
#echo "setting minio test user's password"
./kcadm.sh set-password \
            -r master \
            --username $MINIO_TEST_USER \
            --new-password $MINIO_TEST_USER_PASSWORD

# Create jupyterhub_admins and jupyterhub_staff groups
echo "creating staff groups"
./kcadm.sh create groups -r master -s name=jupyterhub_admins
./kcadm.sh create groups -r master -s name=jupyterhub_staff
echo "created jupyterhub_admins and jupyterhub_staff groups"

# Adds admin user to jupyterhub_admins and jupyterhub_staff groups
MINIO_ADMIN_ID=$(./kcadm.sh get users -r master -q username=$MINIO_TEST_USER | grep id | awk -F'"' '{print $4}')
JUPYTERHUB_ADMINS_GROUP_ID=$(./kcadm.sh get groups -r master | grep jupyterhub_admins -B 1 | grep id | awk -F'"' '{print $4}')
./kcadm.sh update users/$MINIO_ADMIN_ID/groups/$JUPYTERHUB_ADMINS_GROUP_ID -r master -s realm=master -s userId=$MINIO_ADMIN_ID -s groupId=$JUPYTERHUB_ADMINS_GROUP_ID -n

JUPYTERHUB_STAFF_GROUP_ID=$(./kcadm.sh get groups -r master | grep jupyterhub_staff -B 1 | grep id | awk -F'"' '{print $4}')
./kcadm.sh update users/$MINIO_ADMIN_ID/groups/$JUPYTERHUB_STAFF_GROUP_ID -r master -s realm=master -s userId=$MINIO_ADMIN_ID -s groupId=$JUPYTERHUB_STAFF_GROUP_ID -n

# Adds policy=readwrite to staff_group
./kcadm.sh update groups/$JUPYTERHUB_STAFF_GROUP_ID -s 'attributes.policy=["readwrite"]' -r master

# Adds policy=consoleAdmin to the 'admin' user in keycloak, allowing login to minio
#ADMIN_USER_ID=$(./kcadm.sh get users -r master -q username=admin | grep id | awk -F'"' '{print $4}')
./kcadm.sh update users/$ADMIN_USER_ID -r master -s 'attributes.policy=consoleAdmin'
echo "Done initializing keycloak"
