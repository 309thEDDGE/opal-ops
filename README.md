## Opal-Operations
---
#### Purpose

This repo contains all the deployment code and configuration files necessary for deploying Opal platform. The Opal platform consists of Jupyterhub running a custom Jupyter notebook containing TIP. Jupyterhub is also configured with an Externally-Managed Service called Opal-Catalog, which is a custom application built using React and Tornado. The Opal-Catalog application serves data from Catalog-DB stored in Postgresql. Finally, Minio is used as an 'offline bucket' to store parquet files that gets generated by TIP. To control package dependencies and manage the environment in which Jupyterhub and Opal-Catalog run in, Conda is heavily utilized and an extension of Conda called "Conda-Vendor" was created. Conda-Vendor generates local "conda channels", which contains all the necessary packages required for creating the environment in which Jupyterhub and Opal-catalog can successfully run in.

---

#### Instructions for deploying platform locally

1. Clone clone this repo
2. Clone https://github.com/309thEDDGE/opal into this repository's `docker-compose` directory
3. Run the following:

```
cd docker-compose
docker login registry.il2.dso.mil #IL2 IMAGE REGISTRY
docker login registry1.dso.mil #IRONBANK IMAGE REGISTRYs
./start_dev.sh
```
---

#### URLs for local dev

https://minio.127.0.0.1.nip.io/login
https://keycloak.127.0.0.1.nip.io/
https://jupyterhub.127.0.0.1.nip.io/hub/

NOTE: If the links above do not resolve then you will need to modify your hosts file and have minio.127.0.0.1.nip.io, jupyterhub.127.0.0.1.nip.io, keycloak.127.0.0.1.nip.io resolve to localhost.

The user login for jupyterhub:

```
user: opaluser
pass: opalpassword
```

The admin user credentials for keycloak:

```
user: admin
pass: opal
```

#### Adding other users to the deployment

The url pattern for keycloak is `keycloak.<domain>/auth`

Keycloak has a root user and password. These may be obtained as necessary by the admin of the deployment.

To add a user, login to the keycloak url with these root credentials and perform the following:

- Click `Administration Console` (you may automatically be redirected without this step)
- Click `Users`
- Click `Add User`
- Create a username, click save.

After the user is generated, the following steps are performed within the user configuration. If this is not automatically pulled up, it can be accessed by clicking `Users` on the left bar, searching for the username, and clicking the blue UID for the user:

- To allow Minio access, click `Attributes` and add the key `policy` and the value `consoleAdmin`. For less permissive policies see [the minio documentation](https://docs.min.io/minio/baremetal/security/minio-identity-management/policy-based-access-control.html). Ensure `Add` and then `Save` are clicked, otherwise jupyterhub will show a `500: internal Server Error` when the user attempts login
- Click `Groups`, then click `jupyterhub_staff`, then click `join` to allow the user to log into jupyterhub
- Click `Credentials`, add a temporary password in the `Password` and `Password Comfirmation` fields
- Send the username and temporary password to the user

The user should now be able to log into jupyterhub.


#### Instructions for updating base image tags

The `opal-ops/.env` file holds all the references to the base image
tags. To update any of the tags in acceptance, change the tags in this
file and create a Merge Request. An example for updating the tip image is below.

Tag:
```
SINGLE_USER_TIP_IMAGE=registry.il2.dso.mil/skicamp/project-opal/tip:a599b7c2
...
```

New tag:
```
SINGLE_USER_TIP_IMAGE=registry.il2.dso.mil/skicamp/project-opal/tip:b249b7d1
...
```

Create the merge request in a new branch, and then message the ops
team in the `acceptance` channel with a link to the Merge Request.


#### Release format

Releases follow the format `YYYY.MM.DD`.
If a second tag is created in the same day, append with `YYYY.MM.DD_v2`, `YYYY.MM.DD_v3` etc

Do the following to create a tag in the github GUI for opal-ops:

- click `code` 
- click `Releases`
- click `Draft a new release` in the upper right
- add notes in the "release notes" (not messages)

#### Contributing

Prior to pushing any commits to this repository, enable the Trufflehog pre-commit hook with `pre-commit install` from the root of this repository. This will require a working install of docker and [pre-commit](https://pre-commit.com/)

#### Testing the update_deployment.bash

In order to use the test_overwrite_files() located within the update_deployment.bash, you need to ensure the function is uncommented in the main()
and have deepDiff installed locally (use "pip install deepdiff")