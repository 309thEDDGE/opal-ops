# MINIO

* Minio base image -> minio operator
    - https://github.com/minio/operator
    - offloads some ops maintenance
    - supports distributed storage off-the-shelf

# HELM

* Move common services to helm charts
    - Keycloak, postgresql, traefik all have bitnami helm charts
    - Jupyterhub is likely too custom to do this
    - offloads ops maintenance
* Helm chart for opal
    - Jupyterhub, catalog(?)
    - Makes configuration more standardized
* Script for downloading/installing required helm charts
* Readmes for common extensions
    - i.e. gitea