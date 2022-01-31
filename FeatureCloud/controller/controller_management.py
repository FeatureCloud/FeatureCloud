import click
import subprocess
from sys import exit

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
    success, result = controller.start_controller_instance(name, port, data_dir)

    if success:
        click.echo("Controller instance started")
    else:
        click.echo(result)
        exit()


def stop(name: str):
    pass
    # success, result = controller.stop_controller_instance(name)
    # if not success:
    #     click.echo(result)
    #     exit()

def logs(name: str, tail: bool, log_level: str):
    pass

def status(name: str):
    pass

def ls():
    pass
