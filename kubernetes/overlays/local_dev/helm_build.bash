cd $(dirname $0)/../../.. # to opal-ops root

helm template opal \
../argo-helm/charts/argo-workflows \
-f kubernetes/overlays/local_dev/argo_workflows_helm_values.yaml \
> kubernetes/overlays/local_dev/opal_argo_workflows.yaml 

helm template opal \
../metaflow-tools/k8s/helm/metaflow \
-f kubernetes/overlays/local_dev/metaflow_metadata_helm_values.yaml \
> kubernetes/overlays/local_dev/opal_metaflow_metadata.yaml