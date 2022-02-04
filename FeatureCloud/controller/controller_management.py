import click
import docker
import os
import requests
import subprocess
from sys import exit

START_SCRIPT_LOCATION = "./FeatureCloud/controller/start_scripts"
START_SCRIPT_DIR = "./tmp"
START_SCRIPT_NAME = "start_controller"
CONTROLLER_IMAGE = "featurecloud.ai/controller"
CONTROLLER_LABEL = "FCControllerLabel"
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

    # Prune fc controllers
    prune_controllers(name)

    if os.name == 'nt':
        start_script_extension = '.bat'
    else:
        start_script_extension = '.sh'

    start_script_path = prepare_start_script(start_script_extension, name, port, data_dir)

    # Run start script
    if os.name == 'nt':
        p = subprocess.Popen(start_script_path, shell=True, stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        click.echo(p.returncode)
    else:
        subprocess.call(['sh', start_script_path])

def stop(name: str):
    check_controller_prerequisites()
    client = docker.from_env()

    if len(name) == 0:
        name = DEFAULT_CONTROLLER_NAME

    # Removing controllers filtered by name
    for container in client.containers.list(filters={"name": [name]}):
        click.echo("Removing controller with name " + container.name)
        client.api.remove_container(container.id, v=True, force=True)

def prune_controllers(name: str):
    check_controller_prerequisites()
    client = docker.from_env()

    if len(name) == 0:
        name = DEFAULT_CONTROLLER_NAME

    client.containers.prune(filters={"label": [CONTROLLER_LABEL]})

def logs(name: str, tail: bool, log_level: str):
    # get controller address
    check_controller_prerequisites()
    client = docker.from_env()
    try:
        container = client.containers.get(name)
        host_port = container.attrs['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort']
    except docker.errors.NotFound:
        click.echo("Container not found")

    # Get logs content from controller
    params = {'from': 0}
    r = requests.get("http://localhost:" + host_port + "/logs/?from=0")
    click.echo(r.text)


def status(name: str):
    check_controller_prerequisites()
    click.echo(subprocess.check_output(['docker', 'ps', '--filter', 'name=' + name]))

def ls():
    check_controller_prerequisites()
    click.echo(subprocess.check_output(['docker', 'ps', '--filter', 'label=' + CONTROLLER_LABEL]))

def prepare_start_script(start_script_extension: str, name: str, port: int, data_dir: str):
    start_script_path = os.path.join(START_SCRIPT_LOCATION, START_SCRIPT_NAME + start_script_extension)

    # Read in the file
    with open(start_script_path, 'r') as file:
        start_script = file.read()

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

    click.echo("Start script:")
    click.echo(start_script)
    start_script_path = os.path.join(START_SCRIPT_DIR, START_SCRIPT_NAME + start_script_extension)
    # Write the file out again
    with open(start_script_path, 'w') as file:
        file.write(start_script)

    return start_script_path
