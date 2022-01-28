import click
from sys import exit
from FeatureCloud.cli.api import controller
from FeatureCloud.cli import helper


def help():
    print("For registering and testing your apps or using other apps, please visit "
          "our "
          "website: \n https://featurecloud.ai.\n And for more information about"
          " FeatureCloud architecture: \n"
          "The FeatureCloud AI Store for Federated Learning in Biomedicine and "
          "Beyond\n "
          "https://arxiv.org/abs/2105.05734 ")


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


def stop(controller_host: str, test_id: str or int):
    if not controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}.')
        exit()

    success, result = controller.stop_test(controller_host, test_id)
    if not success:
        click.echo(result)
        exit()


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
