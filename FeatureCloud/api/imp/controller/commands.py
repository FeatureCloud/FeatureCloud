
import json
import time

import click
import docker
import os
import tempfile
import requests
import subprocess
from sys import exit

START_SCRIPT_LOCATION = "./FeatureCloud/api/imp/controller/start_scripts"
START_SCRIPT_DIR = "FeatureCloud"
START_SCRIPT_NAME = "start_controller"
CONTROLLER_IMAGE = "featurecloud.ai/controller"
CONTROLLER_LABEL = "FCControllerLabel"
DEFAULT_PORT = 8000
DEFAULT_CONTROLLER_NAME = 'fc-controller'
DEFAULT_DATA_DIR = 'data'
LOG_FETCH_INTERVAL = 3  # seconds
LOG_LEVEL_CHOICES = ['debug', 'info', 'warn', 'error', 'fatal']


def get_docker_client():
    return docker.from_env()

def check_docker_status():
    """Checks whether all docker-related components have been installed."""
    client = get_docker_client()
    try:
        click.echo(client.version)
    except docker.errors.APIError:
        click.echo("Docker daemon is not available")
        exit()


def check_controller_prerequisites():
    check_docker_status()


def start(name: str, port: int, data_dir: str):
    client = get_docker_client()
    check_controller_prerequisites()

    # Create data dir if needed
    try:
        os.mkdir(data_dir)
    except OSError as error:
        pass

    # Prune fc controllers
    prune_controllers(name)

    # Run start script
    pull_proc = client.api.pull(repository='featurecloud.ai/controller', stream=True)
    for p in pull_proc:
        print(p)
    client.containers.run(
            CONTROLLER_IMAGE,
            detach=True,
            name= name if name else DEFAULT_CONTROLLER_NAME,
            ports={8000:port if port else DEFAULT_PORT},
            volumes=[f'{os.getcwd()}/data:/data', '/var/run/docker.sock:/var/run/docker.sock'],
            labels=[CONTROLLER_LABEL],
            command = f"--host-root={os.getcwd()}/data --internal-root=/data --controller-name=fc-controller"
            )

def stop(name: str):
    check_controller_prerequisites()
    client = get_docker_client()

    if len(name) == 0:
        name = DEFAULT_CONTROLLER_NAME

    # Removing controllers filtered by name
    for container in client.containers.list(filters={"name": [name]}):
        click.echo("Removing controller with name " + container.name)
        client.api.remove_container(container.id, v=True, force=True)


def prune_controllers(name: str):
    check_controller_prerequisites()
    client = get_docker_client()

    if not name:
        name = DEFAULT_CONTROLLER_NAME

    client.containers.prune(filters={"label": [CONTROLLER_LABEL]})


def logs(name: str, tail: bool, log_level: str):
    # get controller address
    check_controller_prerequisites()
    client = get_docker_client()
    host_port = 0
    try:
        container = client.containers.get(name)
        host_port = container.attrs['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort']
    except docker.errors.NotFound:
        click.echo("Container not found")
        exit()

    # Get logs content from controller
    lines_fetched = 0
    while True is True:
        url = "http://localhost:" + host_port + "/logs/?from=" + str(lines_fetched)
        r = requests.get(url)
        logs_content = r.json()
        lines_fetched += len(logs_content)
        if len(logs_content) > 0:
            logs_to_display = prepare_logs(logs_content, log_level)
            if len(logs_to_display) > 0:
                click.echo(logs_to_display)
        if not tail:
            break
        time.sleep(LOG_FETCH_INTERVAL)


def status(name: str):
    client = get_docker_client()
    check_controller_prerequisites()
    click.echo(client.containers.get(name))


def ls():
    check_controller_prerequisites()
    click.echo(subprocess.check_output(['docker', 'ps', '--filter', 'label=' + CONTROLLER_LABEL]))


def prepare_start_script(start_script_extension: str, name: str, port: int, data_dir: str):
    start_script_path = os.path.join(START_SCRIPT_LOCATION, START_SCRIPT_NAME + start_script_extension)

    # Read in the file
    with open(start_script_path, 'r') as file:
        start_script = file.read()

    # Stop controllers with the same name
    start_script = start_script.replace("kill " + DEFAULT_CONTROLLER_NAME, "kill " + name)
    start_script = start_script.replace("rm " + DEFAULT_CONTROLLER_NAME, "rm " + name)

    if name != DEFAULT_CONTROLLER_NAME:
        click.echo("Changing default controller name to " + name)
        # For Windows
        start_script = start_script.replace("controllerName=" + DEFAULT_CONTROLLER_NAME, "controllerName=" + name)
        # For MacOS/Linux
        start_script = start_script.replace("--name " + DEFAULT_CONTROLLER_NAME, "--name " + name)
        start_script = start_script.replace("--controller-name=" + DEFAULT_CONTROLLER_NAME, "--controller-name=" + name)

    if port != DEFAULT_PORT:
        click.echo("Changing default port to " + str(port))
        start_script = start_script.replace(str(DEFAULT_PORT) + ":", str(port) + ":")

    if data_dir != DEFAULT_DATA_DIR:
        click.echo("Changing default data dir to " + data_dir)
        start_script = start_script.replace(DEFAULT_DATA_DIR, data_dir)

    start_script_dir = os.path.join(tempfile.gettempdir(), START_SCRIPT_DIR)
    if not os.path.exists(start_script_dir):
        os.makedirs(start_script_dir)
    start_script_path = os.path.join(start_script_dir, START_SCRIPT_NAME + start_script_extension)

    # Write the file out again
    with open(start_script_path, 'w') as file:
        file.write(start_script)

    return start_script_path


def prepare_logs(logs_json, log_level):
    logs_content = ""
    log_level_index = LOG_LEVEL_CHOICES.index(log_level)
    for line in logs_json:
        if LOG_LEVEL_CHOICES.index(line['level']) >= log_level_index:
            logs_content += str(line) + os.linesep
    return logs_content
