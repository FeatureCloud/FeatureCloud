from FeatureCloud.cli.api import controller
from sys import exit

def check_controller_prerequisites():
    return True

def start(name: str, port: int, data_dir: str):
    success, result = controller.start_controller_instance(name, port, data_dir)

    if success:
        click.echo("Controller instance started")
    else:
        click.echo(result)
        exit()


def stop(name: str):
    success, result = controller.stop_controller_instance(name)
    if not success:
        click.echo(result)
        exit()

def logs(name: str, tail: bool, log_level: str):
    pass

def status(name: str):
    pass

def ls():
    pass
