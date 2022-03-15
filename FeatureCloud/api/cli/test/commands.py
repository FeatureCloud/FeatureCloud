import click
from FeatureCloud.api.imp.test import commands

@click.group("test")
def test() -> None:
    """Testbed related commands"""

@test.command('help')
def help():
    _, msg = commands.help()
    click.echo(msg)

@test.command('start')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--client-dirs', default='.,.',
              help='Client directories seperated by comma.',
              required=True)
@click.option('--generic-dir', default='.',
              help='Generic directory available for all clients. Content will be copied to the input folder of all '
                   'instances.',
              required=True)
@click.option('--app-image', default='test_app',
              help='The repository url of the app image.',
              required=True)
@click.option('--channel', default='local',
              help='The communication channel to be used. Can be local or internet.',
              required=True)
@click.option('--query-interval', default=2,
              help='The interval after how many seconds the status call will be performed.',
              required=True)
@click.option('--download-results',
              help='A directory name where to download results. This will be created into /data/tests directory',
              default='')
def start(controller_host: str, client_dirs: str, generic_dir: str, app_image: str, channel: str, query_interval,
          download_results: str):
    _, msg = commands.start(controller_host, client_dirs, generic_dir, app_image, channel, query_interval, download_results)
    click.echo(msg)


@test.command('stop')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be stopped.')
def stop(controller_host: str, test_id: str or int):
    _, msg = commands.stop(controller_host, test_id)
    click.echo(msg)


@test.command('delete')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be deleted. '
                                'To delete all tests omit this option and use "delete all".')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def delete(controller_host: str, test_id: str or int, what: tuple):
    _, msg = commands.delete(controller_host, test_id, what)
    click.echo(msg)


@test.command('list')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--format', help='Format of the test list. json or dataframe', required=True, default='dataframe')
def list(controller_host: str, format: str):
    _, msg = commands.list(controller_host, format)
    click.echo(msg)


@test.command('info')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='Test id', required=True)
@click.option('--format', help='Format of the test info. json or dataframe', required=True, default='dataframe')
def info(controller_host: str, test_id: str or int, format: str):
    _, msg = commands.info(controller_host, test_id, format)
    click.echo(msg)


@test.command('traffic')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be stopped.')
@click.option('--format', help='Format of the test traffic. json or dataframe', required=True, default='dataframe')
def traffic(controller_host: str, test_id: str or int, format: str):
    _, msg = commands.traffic(controller_host, test_id, format)
    click.echo(msg)


@test.command('logs')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test.', required=True)
@click.option('--instance-id', help='The instance id of the client.', required=True)
@click.option('--from-param', help='From param', default='', required=True)
def logs(controller_host: str, test_id: str or int, instance_id: str or int, from_param: str):
    _, msg = commands.logs(controller_host, test_id, instance_id, from_param)
    click.echo(msg)

if __name__ == "__main__":
    test()

