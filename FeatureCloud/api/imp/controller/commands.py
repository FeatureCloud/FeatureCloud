import tqdm
import time
import docker
import os

from FeatureCloud.api.imp.exceptions import FCException, ContainerNotFound
from FeatureCloud.api.imp.test.helper import http

from FeatureCloud.api.imp.util import getcwd_fslash, get_docker_client

DEFAULT_CONTROLLER_IMAGE = "featurecloud.ai/controller"
CONTROLLER_LABEL = "FCControllerLabel"
DEFAULT_PORT = 8000
DEFAULT_CONTROLLER_NAME = 'fc-controller'
DEFAULT_DATA_DIR = 'data'
LOG_FETCH_INTERVAL = 3  # seconds
LOG_LEVEL_CHOICES = ['debug', 'info', 'warn', 'error', 'fatal']


def start(name: str, port: int, data_dir: str, controller_image: str, with_gpu: bool, mount: str, blockchain_address: str):
    client = get_docker_client()

    data_dir = data_dir if data_dir else DEFAULT_DATA_DIR
    controller_image = controller_image if controller_image else DEFAULT_CONTROLLER_IMAGE
    # Create data dir if needed
    try:
        os.mkdir(data_dir)
    except OSError as error:
        pass

    # cleanup unused controller containers
    prune_controllers()

    # remove controller having the same name, if any
    try:
        client.api.remove_container(name, v=True, force=True)
    except docker.errors.NotFound:
        pass
    except docker.errors.DockerException as e:
        raise FCException(e)

    # pull controller and display progress
    try:
        pull_proc = client.api.pull(repository=controller_image, stream=True)
        for p in tqdm.tqdm(pull_proc, desc='Downloading...'):
            pass
    except docker.errors.DockerException as e:
        raise FCException(e)

    cont_name = name if name else DEFAULT_CONTROLLER_NAME
    # forward slash works on all platforms
    base_dir = getcwd_fslash()

    device_requests = None
    gpu_command = ""
    if with_gpu:
        # '--gpus all' option
        device_requests = [docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]
        gpu_command = '--has-gpu'

    blockchain_command = ''
    if blockchain_address:
        blockchain_command = f'--blockchain-address={blockchain_address}'

    volumes = [f'{base_dir}/{data_dir}:/{data_dir}', '/var/run/docker.sock:/var/run/docker.sock']
    if mount:
        volumes.append(f'{mount}:/mnt')

    try:
        client.containers.run(
            controller_image,
            detach=True,
            name=cont_name,
            platform='linux/amd64',
            ports={8000: port if port else DEFAULT_PORT},
            volumes=volumes,
            labels=[CONTROLLER_LABEL],
            device_requests=device_requests,
            command=f"--host-root='{base_dir}/{data_dir}' --internal-root=/{data_dir} --controller-name={cont_name} {gpu_command} {blockchain_command}"
        )
    except docker.errors.DockerException as e:
        raise FCException(e)
    except Exception as e:
        raise FCException(e)


def stop(name: str):
    client = get_docker_client()

    if not name:
        name = DEFAULT_CONTROLLER_NAME

    # Removing controllers filtered by name
    removed = []
    for container in client.containers.list(filters={"name": [name]}):
        try:
            client.api.remove_container(container.id, v=True, force=True)
            removed.append(container.name)
        except docker.errors.DockerException as e:
            raise FCException(e)

    return removed


def prune_controllers():
    client = get_docker_client()

    try:
        client.containers.prune(filters={"label": [CONTROLLER_LABEL]})
    except docker.errors.DockerException as e:
        raise FCException(e)


def logs(name: str, tail: bool, log_level: str):
    client = get_docker_client()

    # get controller address
    host_port = 0
    try:
        container = client.containers.get(name)
        host_port = container.attrs['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort']
    except docker.errors.NotFound:
        raise ContainerNotFound(name)
    except docker.errors.DockerException as e:
        raise FCException(e)

    # Get logs content from controller
    lines_fetched = 0
    while True:
        response = http.get(url=f'http://localhost:{host_port}/logs/?from={lines_fetched}')

        if response.status_code == 200:
            logs_content = response.json()
            lines_fetched += len(logs_content)

            log_level = valid_log_level(log_level)
            filtered = filter_logs(logs_content, log_level)
            for line in filtered:
                yield line
        else:
            raise FCException(response.json('detail'))

        if not tail:
            break
        time.sleep(LOG_FETCH_INTERVAL)


def status(name: str):
    client = get_docker_client()
    try:
        return client.containers.get(name)
    except docker.errors.NotFound:
        raise ContainerNotFound(name)
    except docker.errors.DockerException as e:
        raise FCException(e)


def ls():
    client = get_docker_client()
    try:
        return client.containers.list(filters={'label': [CONTROLLER_LABEL]})
    except docker.errors.DockerException as e:
        raise FCException(e)


def filter_logs(logs_json, log_level):
    log_level_index = LOG_LEVEL_CHOICES.index(log_level)
    return [line for line in logs_json if LOG_LEVEL_CHOICES.index(line['level']) >= log_level_index]


def valid_log_level(log_level):
    if len(log_level) == 0 or log_level not in LOG_LEVEL_CHOICES:
        log_level = LOG_LEVEL_CHOICES[0]

    return log_level
