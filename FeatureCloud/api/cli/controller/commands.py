import os

import click
from FeatureCloud.api.imp.exceptions import FCException

from FeatureCloud.api.imp.controller import commands


@click.group("controller")
def controller() -> None:
    """Controller start/stop. Obtain general information about the controller."""


@controller.command('start')
@click.argument('name', type=str, default=commands.DEFAULT_CONTROLLER_NAME, nargs=1, required=False)
@click.option('--port', default=8000, help='Controller port number. Optional parameter (e.g. --port=8000).', required=False)
@click.option('--data-dir', default='data', help='Controller data directory. Optional parameter (e.g. --data-dir=./data).', required=False)
@click.option('--controller-image', default=commands.DEFAULT_CONTROLLER_IMAGE, help='Controller image name (e.g., featurecloud.ai/controller:latest)', required=False)
@click.option('--gpu', help='Start controller with GPU access. If this succeeds, controller can allow GPU access for apps.', default=False, required=False)
@click.option('--mount', help='Use this option when you want mount a folder that is available only to the '
                              'controller\'s protected environment, e.g. to upload input data for apps.', default='', required=False)
@click.option('--blockchain-address', help='Address of application that connects to the blockchain system', default='', required=False)
def start(name: str, port: int, data_dir: str, controller_image, gpu: bool, mount: str, blockchain_address: str) -> None:
    """Start a controller instance.

    NAME is the controller instance name

    Example: featurecloud controller start my-fc-controller --gpu=True
    """
    try:
        commands.start(name, port, data_dir, controller_image, gpu, mount, blockchain_address)
        click.echo(f'Started controller: {name}')
    except FCException as e:
        if str(e).find("port is already allocated") > -1:
            click.echo(f'Controller could not be started. Port {port} is already allocated.')
        else:
            click.echo(f'Controller could not be started. Error: {e}')


@controller.command('stop')
@click.argument('name', type=str, default=commands.DEFAULT_CONTROLLER_NAME, nargs=1, required=False)
def stop(name: str) -> None:
    """Stop controller instance.

    NAME is the controller instance name

    Example: featurecloud controller stop my-fc-controller
    """

    try:
        result = commands.stop(name)
        if len(result) == 0:
            click.echo(f'No controller found with name {name}')
        else:
            click.echo(f'Stopped controller(s): {",".join(result)}')
    except FCException as e:
        click.echo(f'Controller could not be stopped. Error: {e}')


@controller.command('logs')
@click.argument('name', type=str, default=commands.DEFAULT_CONTROLLER_NAME, nargs=1, required=False)
@click.option('--tail', help='View the tail of controller logs. (e.g. featurecloud controller logs --tail=True)', default=False, required=False)
@click.option('--log-level', default='debug', help='Log level filter. Will filter more sever errors than specified (e.g. featurecloud controller logs  --log-level=debug).', required=False)
def logs(name: str, log_level: str, tail: bool) -> None:
    """Display the logs for the controller instance.

    NAME is the controller instance name.

    Example: featurecloud controller logs my-fc-controller
    """

    try:
        for line in commands.logs(name, tail, log_level):
            click.echo(line)
    except FCException as e:
        click.echo(f'Error: {e}')


@controller.command('status')
@click.argument('name', type=str, default=commands.DEFAULT_CONTROLLER_NAME, nargs=1, required=False)
def status(name: str) -> None:
    """Display general status of the controller.

    NAME is the controller instance name.

    Example: featurecloud controller status my-fc-controller
    """

    try:
        container = commands.status(name)
        click.echo(f'Id: {container.short_id}, Status: {container.status}')
    except FCException as e:
        click.echo(f'Error: {e}')


@controller.command('ls')
def ls() -> None:
    """Lists all running controller instances"""
    try:
        result = commands.ls()
        if len(result) == 0:
            click.echo('No controllers found')
        else:
            for container in result:
                click.echo(f'Id: {container.short_id}, Status: {container.status}')
    except FCException as e:
        click.echo(f'Error: {e}')
