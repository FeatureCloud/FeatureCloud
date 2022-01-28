import click
from FeatureCloud.cli import cli

@click.group("first-level")
def cli() -> None:
    """FeatureCloud pip package"""

@cli.group("test")
def test() -> None:
    """Testbed related commands"""

@test.command('help')
def help():
    cli.help()

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
    cli.start(controller_host, client_dirs, generic_dir, app_image, channel, query_interval, download_results)


@test.command('stop')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be stopped.')
def stop(controller_host: str, test_id: str or int):
    cli.stop(controller_host, test_id)


@test.command('delete')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be deleted. '
                                'To delete all tests omit this option and use "delete all".')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def delete(controller_host: str, test_id: str or int, what: tuple):
    cli.delete(controller_host, test_id, what)


@test.command('list')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--format', help='Format of the test list. json or dataframe', required=True, default='dataframe')
def list(controller_host: str, format: str):
    cli.list(controller_host, format)


@test.command('info')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='Test id', required=True)
@click.option('--format', help='Format of the test info. json or dataframe', required=True, default='dataframe')
def info(controller_host: str, test_id: str or int, format: str):
    cli.info(controller_host, test_id, format)


@test.command('traffic')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be stopped.')
@click.option('--format', help='Format of the test traffic. json or dataframe', required=True, default='dataframe')
def traffic(controller_host: str, test_id: str or int, format: str):
    cli.traffic(controller_host, test_id, format)


@test.command('logs')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test.', required=True)
@click.option('--instance-id', help='The instance id of the client.', required=True)
@click.option('--from-param', help='From param', default='', required=True)
def logs(controller_host: str, test_id: str or int, instance_id: str or int, from_param: str):
    cli.logs(controller_host, test_id, instance_id, from_param)

@cli.group("workflow")
def workflow() -> None:
    """Workflow related commands"""

@workflow.command('workflow')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--wf-dir', default='.,.',
              help='workflow path',
              required=True)
@click.option('--channel', default='local',
              help='The communication channel to be used. Can be local or internet.',
              required=True)
@click.option('--query-interval', default=2,
              help='The interval after how many seconds the status call will be performed.',
              required=True)
def workflow(controller_host: str, wf_dir: str, channel: str, query_interval):
    # from
    pass

@cli.group("controller")
def controller()-> None:
    """Controller start/stop"""

@controller.command()
def start() -> None:
    """Start controller"""

@controller.command()
def stop() -> None:
    """Stop controller"""

if __name__ == "__main__":
    cli()
