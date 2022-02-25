import click
from FeatureCloud.cli import cli
from FeatureCloud.controller import controller_management
import sys
import importlib


@click.group("first-level")
def fc_cli() -> None:
    """FeatureCloud pip package"""


@fc_cli.group("test")
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
def list_tests(controller_host: str, format: str):
    cli.list_tests(controller_host, format)


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


@fc_cli.group("workflow")
def workflow() -> None:
    """Workflow related commands"""


@workflow.command('start')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--wf-dir', default='',
              help='path to directory containing the workflow',
              required=True)
@click.option('--wf-file', default='example_wf',
              help='python file including the workflow',
              required=True)
@click.option('--channel', default='local',
              help='The communication channel to be used. Can be local or internet.',
              required=True)
@click.option('--query-interval', default=1,
              help='The interval after how many seconds the status call will be performed.',
              required=True)
def start_workflow(controller_host: str, wf_dir: str, wf_file: str, channel: str, query_interval: str):
    sys.path.append(wf_dir)
    workflow_class = importlib.import_module(wf_file)
    wf = workflow_class.WorkFlow(controller_host=controller_host, channel=channel, query_interval=query_interval)
    wf.register_apps()
    wf.run()


@fc_cli.group("controller")
def controller() -> None:
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


if __name__ == "__main__":
    fc_cli()
