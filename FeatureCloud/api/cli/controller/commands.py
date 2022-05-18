import os

import click
from FeatureCloud.api.imp.exceptions import FCException

from FeatureCloud.api.imp.controller import commands

@click.group("controller")
def controller() -> None:
    """Controller start/stop"""


@controller.command('start')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
@click.option('--port', default=8000, help='Controller port number.', required=False)
@click.option('--data-dir', default='data', help='Controller data directory.', required=False)
def start(what: tuple, port: int, data_dir: str) -> None:
    """Start controller"""
    name = commands.DEFAULT_CONTROLLER_NAME
    if len(what) > 0:
        name = what[0]
    try:
        commands.start(name, port, data_dir)
        click.echo(f'Started controller: {name}')
    except FCException as e:
        click.echo(f'Error: {e}')


@controller.command('stop')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def stop(what: tuple) -> None:
    """Stop controller instance"""
    name = commands.DEFAULT_CONTROLLER_NAME
    if len(what) > 0:
        name = what[0]

    try:
        result = commands.stop(name)
        if len(result) == 0:
            click.echo(f'No controller found with name {name}')
        else:
            click.echo(f'Stopped controller(s): {",".join(result)}')
    except FCException as e:
        click.echo(f'Error: {e}')


@controller.command('logs')
@click.option('--tail', help='View the tail of controller logs.', default=False, required=False)
@click.option('--log-level', default='debug', help='Log level filter.')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def logs(what: tuple, log_level: str, tail: bool) -> None:
    """Display the logs for the controller instance"""
    name = commands.DEFAULT_CONTROLLER_NAME
    if len(what) > 0:
        name = what[0]

    try:
        for line in commands.logs(name, tail, log_level):
            click.echo(line)
    except FCException as e:
        click.echo(f'Error: {e}')


@controller.command('status')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def status(what: tuple) -> None:
    """Display general status of the controller"""
    name = commands.DEFAULT_CONTROLLER_NAME
    if len(what) > 0:
        name = what[0]

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
