# local testing

Make sure you log into the appropriate image registeries before running docker-compose so that the images are pulled down successfully. Then start docker-compose by running the start_dev.sh:

```shell
docker login registry.il2.dso.mil #IL2 IMAGE REGISTRY
docker login registry1.dso.mil #IRONBANK IMAGE REGISTRY
./start_dev.sh
```
