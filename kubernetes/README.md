# OPAL for Kubernetes

To start: `bash start_aws_k8.bash`

## Components

Each file contains its Service and Deployment definitions along with any other configurations/volumes needed to run it.

- jupyterhub.yaml
- postgres.yaml
- minio.yaml
- keycloak.yaml
- traefik.yaml
- catalog.yaml (WIP)

## Other stuff
- init_singleuser_image.yaml
    - A DaemonSet that pulls the tip singleuser image to all nodes so that a jupyterhub server can always be quickly created on any node
- init_singleuser_image_pytorch.yaml
    - Same concept as above, but builds the pytorch singleuser image

## Notes:   

### AWS EKS EBS CSI Driver

(Amazon web service) (elastic kubernetes service) (elastic block storage) (container storage interface) driver

Aside from being acronym soup, this cluster driver needs to be running for the EKS cluster to dynamically provision persistent volumes for persistent volume claims. The driver needs certain permissions in order to actually create the volumes. It's a bit of an ordeal to set up. More details here: https://docs.aws.amazon.com/eks/latest/userguide/managing-ebs-csi.html

### Jupyterhub Public Proxy Service HTTPS Disabled

The service to the proxy won't work if you enable the HTTPS port for now, will probably be fixed once certs are figured out.

### Quick hub restart command

`bash ./start_aws_k8.bash && kubectl delete pod $(kubectl get pods -o json | jq -r '.items[] | select(.metadata.name | test("hub-")).metadata.name') && kubectl get pod`