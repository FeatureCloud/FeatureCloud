# import argparse
import os
import subprocess
import sys

# parser = argparse.ArgumentParser(description="For registering and testing your apps or using other apps, please visit "
#                                              "our "
#                                              "website: \n https://featurecloud.ai.\n And for more information about"
#                                              " FeatureCloud architecture: \n"
#                                              "The FeatureCloud AI Store for Federated Learning in Biomedicine and "
#                                              "Beyond\n "
#                                              "https://arxiv.org/abs/2105.05734 ",
#                                  )
# parser.add_argument("--echo", type=str, default=None, help="Get an input and print it!")
# parser.add_argument('--delete', '--del', default=None, type=str, help='Delete a the given test run')
# parser.add_argument('--info', type=str, default=None, help='Get details about the given test run')
# parser.add_argument('--list', dest='list', help='List all test runs', action='store_true', default=False)
# parser.add_argument('--logs', type=str, default=None, help='Get the logs of the given test runs')
# parser.add_argument('--start', type=str, default=None, help='Start the given test run')
# parser.add_argument('--stop', type=str, default=None, help='Stop the given test run')
# parser.add_argument('--traffic', type=str, default=None, help='Show the traffic of a single test run')


import click
from sys import exit
from FeatureCloud.cli.api import controller
from FeatureCloud.cli import helper


@click.group()
def test():
    pass


@test.command('help')
def help():
    print("For registering and testing your apps or using other apps, please visit "
          "our "
          "website: \n https://featurecloud.ai.\n And for more information about"
          " FeatureCloud architecture: \n"
          "The FeatureCloud AI Store for Federated Learning in Biomedicine and "
          "Beyond\n "
          "https://arxiv.org/abs/2105.05734 ")

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
    if not controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = controller.start_test(controller_host,
                                            app_image,
                                            filter(None, client_dirs.split(',')),
                                            generic_dir,
                                            channel == 'local',
                                            query_interval,
                                            download_results)

    if success:
        click.echo(result['id'])
        return result['id']
    else:
        click.echo(result)
        exit()


@test.command('stop')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be stopped.')
def stop(controller_host: str, test_id: str or int):
    if not controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}.')
        exit()

    success, result = controller.stop_test(controller_host, test_id)
    if not success:
        click.echo(result)
        exit()


@test.command('delete')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be deleted. '
                                'To delete all tests omit this option and use "delete all".')
@click.argument('what', nargs=-1)  # using variadic arguments to make it not required
def delete(controller_host: str, test_id: str or int, what: tuple):
    if not controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}.')
        exit()

    if test_id is not None and len(what) == 0:
        success, result = controller.delete_test(controller_host, test_id)

        if not success:
            click.echo(result['detail'])
            exit()

    elif test_id is None and len(what) > 0:
        if what[0].lower() == 'all':
            success, result = controller.delete_tests(controller_host)

            if not success:
                click.echo(result['detail'])
                exit()
        else:
            click.echo(f'Unsupported argument {what[0]}')
            exit()

    else:
        click.echo('Wrong combination of parameters. '
                   'To delete a single test use option --test-id. To delete all tests use the "all" argument.')
        exit()


@test.command('list')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--format', help='Format of the test list. json or dataframe', required=True, default='dataframe')
def list(controller_host: str, format: str):
    if not controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = controller.get_tests(controller_host)
    if success:
        if len(result) == 0:
            click.echo('No tests available.')
            exit()
        if format == 'json':
            click.echo(result)
            return result
        elif format == 'dataframe':
            df = helper.json_to_dataframe(result).set_index('id')
            click.echo(df.to_string())
            return df
        else:
            click.echo(f'Format {format} not available. Returning json.')
            click.echo(result)
            return result
    else:
        click.echo(result)
        exit()


@test.command('info')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='Test id', required=True)
@click.option('--format', help='Format of the test info. json or dataframe', required=True, default='dataframe')
def info(controller_host: str, test_id: str or int, format: str):
    if not controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = controller.get_test(controller_host, test_id)
    if success:
        if format == 'json':
            click.echo(result)
            return result
        elif format == 'dataframe':
            df = helper.json_to_dataframe(result, single_entry=True).set_index('id')
            click.echo(df.to_string())
            return df
        else:
            click.echo(f'Format {format} not available. Returning json.')
            return result
    else:
        click.echo(result['detail'])
        exit()


@test.command('traffic')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be stopped.')
@click.option('--format', help='Format of the test traffic. json or dataframe', required=True, default='dataframe')
def traffic(controller_host: str, test_id: str or int, format: str):
    if not controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = controller.get_traffic(controller_host, test_id)
    if success:
        if format == 'json':
            click.echo(result)
            return result
        elif format == 'dataframe':
            df = helper.json_to_dataframe(result)
            click.echo(df.to_string())
            return df
        else:
            click.echo(f'Format {format} not available. Returning json.')
            return result
    else:
        click.echo(result['detail'])
        exit()


@test.command('logs')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test.', required=True)
@click.option('--instance-id', help='The isntance id of the client.', required=True)
@click.option('--from-param', help='From param', default='', required=True)
def logs(controller_host: str, test_id: str or int, instance_id: str or int, from_param: str):
    if not controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = controller.get_logs(controller_host, test_id, instance_id, from_param)
    if success:
        for line in result["logs"].split("\n"):
            click.echo(line)
        return result
    else:
        click.echo(result['detail'])
        exit()

# def fc_command():
#     args = parser.parse_args()
#
#     python = sys.executable
#     details = subprocess.check_output([python, '-m', 'pip', 'show', 'FeatureCloud'])
#     path = None
#     for pair in details.decode('utf-8').strip().split("\n"):
#         if "location:" in pair.lower():
#             path = pair.strip().split(":")[-1].strip()
#     if path is None:
#         raise KeyError("There is no location")
#
#     cli = f"{path}/FeatureCloud/cli/cli.py"
#     options = vars(args)
#     print(options[0])
#     print(len(options))
#     for k, v in vars(args).items():
#         if v is not None:
#             if k == 'echo':
#                 print(v)
#             elif k == 'list':
#                 if v:
#                     os.system(f'{python} {cli} {k}')
#             else:
#
#                 os.system(f'{python} {cli} {k} {v}')
