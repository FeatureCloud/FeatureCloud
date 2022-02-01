import os

import click
import docker
import subprocess
from sys import exit

import requests
from docker.types import Mount

CONTROLLER_IMAGE = "featurecloud.ai/controller"
CONTROLLER_LABEL = "fc-controller-label"
DEFAULT_PORT = 8000
DEFAULT_CONTROLLER_NAME = 'fc-controller'
DEFAULT_DATA_DIR = 'data'

def check_docker_status():
    """Checks whether all docker-related components have been installed."""
    try:
        subprocess.check_output(['docker', '--version'])
    except OSError:
        click.echo("Docker daemon is not available")
        exit()

def check_controller_prerequisites():
    check_docker_status()

def start(name: str, port: int, data_dir: str):
    check_controller_prerequisites()

    # Create data dir if needed
    try:
        os.mkdir(data_dir)
    except OSError as error:
        pass

    if os.name == 'nt':
        script_extension = 'bat'
    else:
        script_extension = 'sh'

    # Download start script from server
    download("https://featurecloud.ai/assets/scripts/start_controller." + script_extension, "./FeatureCloud/controller")

    replace_options_in_start_script(name, port, data_dir)

    # Run start script
    if os.name == 'nt':
        subprocess.call([r'./FeatureCloud/controller/start_controller.bat'])
    else:
        subprocess.call(['sh', './FeatureCloud/controller/start_controller.sh'])

def stop(name: str):
    check_controller_prerequisites()

    client = docker.from_env()
    for container in client.containers.list():
        if container.image == CONTROLLER_IMAGE:
            client.api.remove_container(container, v=True, force=True)

def logs(name: str, tail: bool, log_level: str):
    pass

def status(name: str):
    pass

def ls():
    pass

def download(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))

def replace_options_in_start_script(name: str, port: int, data_dir: str):
    if name != DEFAULT_CONTROLLER_NAME:
        pass

    if port != DEFAULT_PORT:
        pass

    if data_dir != DEFAULT_DATA_DIR:
        pass
