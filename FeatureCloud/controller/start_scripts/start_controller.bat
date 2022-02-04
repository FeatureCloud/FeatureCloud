SET basePath=%cd%
SET controllerName=fc-controller

mkdir data

docker kill %controllerName%
docker rm %controllerName%
docker pull featurecloud.ai/controller

docker run ^
-l FCControllerLabel ^
-d ^
-p 8000:8000 ^
--name %controllerName% ^
-v "/var/run/docker.sock:/var/run/docker.sock" ^
--mount "type=bind,source=%basePath%/data,target=/data" ^
featurecloud.ai/controller "--host-root=%basePath%/data" "--internal-root=/data" "--controller-name=%controllerName%"
