mkdir -p data

docker kill fc-controller > /dev/null 2>&1
docker rm fc-controller > /dev/null 2>&1
docker pull featurecloud.ai/controller

docker run \
 -l FCControllerLabel \
 -d \
 -p 8000:8000 \
 --name fc-controller \
 -v "/var/run/docker.sock:/var/run/docker.sock" \
 --mount "type=bind,source=$(pwd)/data,target=/data" \
 featurecloud.ai/controller "--host-root=$(pwd)/data" "--internal-root=/data" "--controller-name=fc-controller"
