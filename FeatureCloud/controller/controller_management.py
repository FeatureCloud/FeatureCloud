import click
import docker
import os
import requests
import subprocess
from sys import exit

START_SCRIPT_DIR = "./tmp"
START_SCRIPT_NAME = "start_controller"
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

    # Prune fc controllers
    stop_all_controllers(name)

    if os.name == 'nt':
        start_script_extension = '.bat'
    else:
        start_script_extension = '.sh'

    # Download start script from server
    download("https://featurecloud.ai/assets/scripts/start_controller" + start_script_extension, START_SCRIPT_DIR)

    start_script_path = os.path.join(START_SCRIPT_DIR, START_SCRIPT_NAME + start_script_extension)
    replace_options_in_start_script(start_script_path, name, port, data_dir)

    # Run start script
    if os.name == 'nt':
        subprocess.call([r'./FeatureCloud/controller/start_controller.bat'])
    else:
        subprocess.call(['sh', './FeatureCloud/controller/start_controller.sh'])

def stop(name: str):
    check_controller_prerequisites()
    client = docker.from_env()

    if len(name) == 0:
        name = DEFAULT_CONTROLLER_NAME

    # Removing controllers filtered by name
    for container in client.containers.list(filters={"name": [name]}):
        click.echo("Removing controller with label" + CONTROLLER_LABEL + " and name " + container.name)
        client.api.remove_container(container.id, v=True, force=True)

def stop_all_controllers(name: str):
    check_controller_prerequisites()
    client = docker.from_env()

    if len(name) == 0:
        name = DEFAULT_CONTROLLER_NAME

    client.containers.prune(filters={"label": [CONTROLLER_LABEL]})

    # Removing controllers filtered by name
    for container in client.containers.list(filters={"name": [name]}):
        click.echo("Removing controller with label " + CONTROLLER_LABEL + " and name " + container.name)
        client.api.remove_container(container.id, v=True, force=True)

    # Removing controllers filtered by label
    for container in client.containers.list(filters={"label": [CONTROLLER_LABEL]}):
        click.echo("Removing controller with label" + CONTROLLER_LABEL + " and name " + container.name)
        client.api.remove_container(container.id, v=True, force=True)

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
        print("Saving start script to ", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))

def replace_options_in_start_script(start_script_path: str, name: str, port: int, data_dir: str):
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

    # Configure label
    start_script = start_script.replace('docker run ', 'docker run -l ' + CONTROLLER_LABEL + " ")

    click.echo("Final start script:")
    click.echo(start_script)
    # Write the file out again
    with open(start_script_path, 'w') as file:
        file.write(start_script)
