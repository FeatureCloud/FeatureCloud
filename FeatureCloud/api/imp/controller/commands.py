import tqdm
import json
import time

import click
import docker
import os
import tempfile
import requests
import subprocess
from sys import exit

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
    for p in tqdm.tqdm(pull_proc, desc='Downloading...'):
        pass
    client.containers.run(
            CONTROLLER_IMAGE,
            detach=True,
            name= name if name else DEFAULT_CONTROLLER_NAME,
            platform='linux/amd64',
            ports={8000:port if port else DEFAULT_PORT},
            volumes=[f'{os.getcwd()}/data:/data', '/var/run/docker.sock:/var/run/docker.sock'],
            labels=[CONTROLLER_LABEL],
            command = f"--host-root={os.getcwd()}/data --internal-root=/data --controller-name=fc-controller"
            )

def stop(name: str):
    check_controller_prerequisites()
    client = get_docker_client()

    if name:
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
    client = get_docker_client()
    click.echo(client.containers.list(filters={'label': [CONTROLLER_LABEL]}))


def prepare_logs(logs_json, log_level):
    logs_content = ""
    log_level_index = LOG_LEVEL_CHOICES.index(log_level)
    for line in logs_json:
        if LOG_LEVEL_CHOICES.index(line['level']) >= log_level_index:
            logs_content += str(line) + os.linesep
    return logs_content
