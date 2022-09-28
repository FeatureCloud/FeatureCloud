import os

import click
import requests

from FeatureCloud.api.imp.exceptions import FCException

from FeatureCloud.api.imp.test import commands
from FeatureCloud.api.cli.test.workflow.commands import workflow


@click.group("test")
def test() -> None:
    """Testbed related commands"""


test.add_command(workflow)


@test.command('help')
def help():
    _, msg = commands.help()
    click.echo(msg)


@test.command('start')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance (e.g. featurecloud test start --controller-host=http://localhost:8000).',
              required=True)
@click.option('--client-dirs', default='.,.',
              help='Client directories separated by comma. The number of clients is based on the number of directories supplied here (e.g. `featurecloud test start --client-dirs=.,.,.,.` command will start 4 clients).',
              required=True)
@click.option('--generic-dir', default='.',
              help='Generic directory available for all clients. Content will be copied to the input folder of all '
                   'instances (e.g. featurecloud test start --generic-dir=.).',
              required=True)
@click.option('--app-image', default='test_app',
              help='The repository url of the app image (e.g. featurecloud test start --app-image=featurecloud.ai/test_app).',
              required=True)
@click.option('--channel', default='local',
              help='The communication channel to be used. Possible values: "local" or "internet" (e.g. featurecloud test start --channel=local).',
              required=True)
@click.option('--query-interval', default=2.0,
              help='The interval after how many seconds the status call will be performed (e.g. featurecloud test start --query-interval=2).',
              required=True)
@click.option('--download-results',
              help='A directory name where to download results. This will be created into /data/tests directory (e.g. featurecloud test start --download-results=./results).',
              default='')
def start(controller_host: str, client_dirs: str, generic_dir: str, app_image: str, channel: str, query_interval: str,
          download_results: str):
    """Starts testbed run with the specified parameters"""
    try:
        result = commands.start(controller_host, client_dirs, generic_dir, app_image, channel, query_interval,
                                download_results)
        click.echo(f"Test id={result} started")
    except requests.exceptions.InvalidSchema:
        click.echo(f'No connection adapters were found for {controller_host}')
    except requests.exceptions.MissingSchema:
        click.echo(f' Invalid URL {controller_host}: No scheme supplied. Perhaps you meant http://{controller_host}?')
    except FCException as e:
        click.echo(f'Error: {e}')


@test.command('stop')
@click.option('--controller-host', default='http://localhost:8000',
              help='Http address of your running controller instance (e.g. featurecloud test stop --controller-host=http://localhost:8000).',
              required=True)
@click.option('--test-id', help='The test id of the test to be stopped. The test id is returned by the start command (e.g.featurecloud test stop --test-id=1).')
def stop(controller_host: str, test_id: str or int):
    '''Stops test with specified test id'''
    try:
        result = commands.stop(controller_host, test_id)
        click.echo(f"Test id={result} stopped")
    except requests.exceptions.InvalidSchema:
        click.echo(f'No connection adapters were found for {controller_host}')
    except requests.exceptions.MissingSchema:
        click.echo(f' Invalid URL {controller_host}: No scheme supplied. Perhaps you meant http://{controller_host}?')
    except FCException as e:
        click.echo(f'Error: {e}')


@test.command('delete')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.  (e.g. featurecloud test delete all --controller-host=http://localhost:8000)',)
@click.option('--test-id', help='The test id of the test to be deleted. The test id is returned by the start command.'
                                'To delete all tests omit this option and use "delete all".')
@click.argument('all', type=str, nargs=1, required=False)
def delete(controller_host: str, test_id: str or int, all: str):
    '''
    Deletes test with specified id or alternatively, deletes all tests

     ALL - delete all tests

     Examples:

         featurecloud test delete --test-id=1

         featurecloud test delete all
    '''
    try:
        result = commands.delete(controller_host, test_id, all)
        if all is not None:
            if all.lower() == 'all':
                click.echo(f"All tests deleted")
            else:
                click.echo(f'Wrong parameter {all}')
        else:
            click.echo(f"Test id={result} deleted")
    except requests.exceptions.InvalidSchema:
        click.echo(f'No connection adapters were found for {controller_host}')
    except requests.exceptions.MissingSchema:
        click.echo(f' Invalid URL {controller_host}: No scheme supplied. Perhaps you meant http://{controller_host}?')
    except FCException as e:
        click.echo(f'Error: {e}')


@test.command('list')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance (e.g. featurecloud test list --controller-host=http://localhost:8000).',
              required=True)
@click.option('--format', help='Format of the test list. Possible options: json or dataframe (e.g. featurecloud test list --format=dataframe).', required=True, default='dataframe')
def list(controller_host: str, format: str):
    '''List all tests'''
    try:
        result = commands.list(controller_host, format)
        if len(result) == 0:
            click.echo('No tests available')
        else:
            click.echo(result)
    except requests.exceptions.InvalidSchema:
        click.echo(f'No connection adapters were found for {controller_host}')
    except requests.exceptions.MissingSchema:
        click.echo(f' Invalid URL {controller_host}: No scheme supplied. Perhaps you meant http://{controller_host}?')
    except FCException as e:
        click.echo(f'Error: {e}')


@test.command('info')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance (e.g. featurecloud test info --controller-host=http://localhost:8000).',
              required=True)
@click.option('--test-id', help='Test id to get info about (e.g. featurecloud test info --test-id=1).', required=True)
@click.option('--format', help='Format of the test info. Possible values: json or dataframe (e.g. featurecloud test info --format=dataframe).', required=True, default='dataframe')
def info(controller_host: str, test_id: str or int, format: str):
    '''Get information about a running test'''
    try:
        result = commands.info(controller_host, test_id, format)
        click.echo(result)
    except requests.exceptions.InvalidSchema:
        click.echo(f'No connection adapters were found for {controller_host}')
    except requests.exceptions.MissingSchema:
        click.echo(f' Invalid URL {controller_host}: No scheme supplied. Perhaps you meant http://{controller_host}?')
    except FCException as e:
        click.echo(f'Error: {e}')


@test.command('traffic')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance (e.g. featurecloud test traffic --controller-host=http://localhost:8000).',
              required=True)
@click.option('--test-id', help='The test id to get traffic info about (e.g. featurecloud test traffic --test-id=1).')
@click.option('--format', help='Format of the test traffic. Possible values: json or dataframe (e.g. featurecloud test traffic --format=dataframe).e', required=True, default='dataframe')
def traffic(controller_host: str, test_id: str or int, format: str):
    '''Displays traffic information inside tests'''
    try:
        result = commands.traffic(controller_host, test_id, format)
        click.echo(result)
    except requests.exceptions.InvalidSchema:
        click.echo(f'No connection adapters were found for {controller_host}')
    except requests.exceptions.MissingSchema:
        click.echo(f' Invalid URL {controller_host}: No scheme supplied. Perhaps you meant http://{controller_host}?')
    except FCException as e:
        click.echo(f'Error: {e}')


@test.command('logs')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance (e.g. featurecloud test logs --controller-host=http://localhost:8000).',
              required=True)
@click.option('--test-id', help='The test id to get logs about (e.g. featurecloud test logs --test-id=1).', required=True)
@click.option('--instance-id', help='The instance id of the test client. Instance ids can be obtained by running the info command (e.g. featurecloud test logs --test-id=1 --instance-id=0).', required=True)
@click.option('--from-row', help='Get logs from a certain row number (e.g. featurecloud test logs --test-id=1 --instance-id=0 --from-row=0).', default='', required=True)
def logs(controller_host: str, test_id: str or int, instance_id: str or int, from_row: str):
    '''Get logs from test client'''
    try:
        result = commands.logs(controller_host, test_id, instance_id, from_row)
        log_lines = ""
        for line in result:
            log_lines += str(line) + os.linesep
        click.echo(log_lines)
    except requests.exceptions.InvalidSchema:
        click.echo(f'No connection adapters were found for {controller_host}')
    except requests.exceptions.MissingSchema:
        click.echo(f' Invalid URL {controller_host}: No scheme supplied. Perhaps you meant http://{controller_host}?')
    except FCException as e:
        click.echo(f'Error: {e}')


if __name__ == "__main__":
    test()
