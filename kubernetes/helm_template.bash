# be in the kubernetes folder
cd $(dirname $0)

ARGO_HOME=../../argo-helm/charts
METAFLOW_HOME=../../metaflow-tools/k8s/helm/metaflow

# `helm template` fills out the helm chart with the
# values defined in the file after `-f` and streams
# the output to stdout

helm template opal $ARGO_HOME/argo-cd \
-f argocd/argo_cd_helm_values.yaml \
> argocd/opal_argo_cd.yaml

helm template opal $ARGO_HOME/argo-workflows \
-f overlays/local_dev/argo_workflows_helm_values.yaml \
> overlays/local_dev/kubernetes_files/opal_argo_workflows.yaml

helm template opal $METAFLOW_HOME \
-f overlays/local_dev/metaflow_metadata_helm_values.yaml \
> overlays/local_dev/kubernetes_files/opal_metaflow_metadata.yaml
