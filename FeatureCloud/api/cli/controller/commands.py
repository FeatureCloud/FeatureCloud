import click
from FeatureCloud.api.utils.controller import controller_management

@click.group("controller")
def controller()-> None:
    """Controller start/stop"""

@controller.command('start')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
@click.option('--port', default=8000, help='Controller port number.', required=False)
@click.option('--data-dir', default='data', help='Controller data directory.', required=False)
def start(what: tuple, port: int, data_dir: str) -> None:
    """Start controller"""
    name = controller_management.DEFAULT_CONTROLLER_NAME
    if len(what) > 0:
        name = what[0]
    controller_management.start(name, port, data_dir)

@controller.command('stop')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def stop(what: tuple) -> None:
    """Stop controller instance"""
    name = controller_management.DEFAULT_CONTROLLER_NAME
    if len(what) > 0:
        name = what[0]
    controller_management.stop(name)

@controller.command('logs')
@click.option('--tail', help='View the tail of controller logs.', default=False, required=False)
@click.option('--log-level', default='debug', help='Log level filter.')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def logs(what: tuple, log_level: str, tail: bool) -> None:
    """Display the logs for the controller instance"""
    name = controller_management.DEFAULT_CONTROLLER_NAME
    if len(what) > 0:
        name = what[0]
    log_level_choices = ['debug', 'info', 'warn', 'error', 'fatal']
    if len(log_level) == 0 or log_level not in log_level_choices:
        log_level = log_level_choices[0]
    controller_management.logs(name, tail, log_level)


@controller.command('status')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def status(what: tuple) -> None:
    """Display general status of the controller"""
    name = controller_management.DEFAULT_CONTROLLER_NAME
    if len(what) > 0:
        name = what[0]
    controller_management.status(name)

@controller.command('ls')
def ls() -> None:
    """Lists all running controller instances"""
    controller_management.ls()
