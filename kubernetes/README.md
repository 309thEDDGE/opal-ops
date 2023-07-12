# OPAL for Kubernetes

Requirements:
- kubectl
- minikube

To start: `bash start_local.bash`

## Description

### Components

Each file contains its Service and Deployment definitions along with any other configurations/volumes needed to run it.

- jupyterhub.yaml
- postgres.yaml
- minio.yaml
- keycloak.yaml
- traefik.yaml

### Overlays

Kustomize overlays must define the following to work:
- k8.env (deployment-specific environment variables)
- ingress.yaml (DNS endpoints, used by traefik)
- A daemonset that pulls the singleuser image (see below)

### Other stuff

- init_singleuser_image.yaml (local)
    - A DaemonSet that pulls the tip singleuser image to all nodes so that a jupyterhub server can always be quickly created on any node
- init_singleuser_image_pytorch.yaml (aws)
    - Same concept as above, but builds the pytorch singleuser image

## Customization

### Endpoint Domain Name

To change the endpoint, the following environment variables in the overlay's k8.env need to be changed to match:
- KEYCLOAK_AUTH_SERVER_URL
- KEYCLOAK_CALLBACK_URL
- OPAL_CATALOG_CALLBACK
- KEYCLOAK_JUPYTERHUB_OAUTH_CALLBACK
- KEYCLOAK_JUPYTERHUB_USERDATA_URL
- KEYCLOAK_OPAL_API_URL
- MINIO_IDENTITY_OPENID_URL
- MINIO_IDENTITY_OPENID_REDIRECT_URI
- MINIO_BROWSER_REDIRECT_URL

The entries in ingress.yaml under spec.rules.*.host also need to be changed.

### Banner

The OPAL_BANNER_TEXT and OPAL_BANNER_COLOR variables in the k8.env file for the overlay used can be modified to change the appearance of the banner.

### Single User or Pytorch Image

The image tags in both the k8.env file and the image initialization daemonset for the overlay used must be changed together to be updated.

### Single User Environment Variables

The jupyterhub_config.py file in base/extra_resources has all the machinery to set up the single user environments. `c.KubeSpawner.environment` on line 42 has basic environment variable definitions. `c.KubeSpawner.env_keep` on line 32 will transfer environment variables from the Jupyterhub deployment to single user containers.

## Notes:   

### AWS EKS EBS CSI Driver

(Amazon web service) (elastic kubernetes service) (elastic block storage) (container storage interface) driver

Aside from being acronym soup, this cluster driver needs to be running for the EKS cluster to dynamically provision persistent volumes for persistent volume claims. The driver needs certain permissions in order to actually create the volumes. It's a bit of an ordeal to set up. More details here: https://docs.aws.amazon.com/eks/latest/userguide/managing-ebs-csi.html

### Jupyterhub Public Proxy Service HTTPS Disabled

The service to the proxy won't work if you enable the HTTPS port. This is OK because Traefik handles TLS certificates and HTTPS routing.
