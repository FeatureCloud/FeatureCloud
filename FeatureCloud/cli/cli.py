import click
from sys import exit
from FeatureCloud.cli import api
import helper


@click.group()
def test():
    pass


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
    if not api.controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = api.controller.start_test(controller_host,
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
    if not api.controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}.')
        exit()

    success, result = api.controller.stop_test(controller_host, test_id)
    if not success:
        click.echo(result)
        exit()


@test.command('delete')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--test-id', help='The test id of the test to be stopped.')
def delete(controller_host: str, test_id: str or int):
    if not api.controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}.')
        exit()
    success, result = api.controller.delete_test(controller_host, test_id)

    if not success:
        click.echo(result['detail'])
        exit()


@test.command('list')
@click.option('--controller-host', default='http://localhost:8000',
              help='Address of your running controller instance.',
              required=True)
@click.option('--format', help='Format of the test list. json or dataframe', required=True, default='dataframe')
def list(controller_host: str, format: str):
    if not api.controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = api.controller.get_tests(controller_host)
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
    if not api.controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = api.controller.get_test(controller_host, test_id)
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
    if not api.controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = api.controller.get_traffic(controller_host, test_id)
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
    if not api.controller.is_online(controller_host):
        click.echo(f'No controller online on {controller_host}. Exiting.')
        exit()

    success, result = api.controller.get_logs(controller_host, test_id, instance_id, from_param)
    if success:
        for line in result["logs"].split("\n"):
            click.echo(line)
        return result
    else:
        click.echo(result['detail'])
        exit()


# @click.group()
# def workflow():
#     pass
#
#
# @workflow.command('info')
# @click.option('--project_id', help='ID of the project.', required=True)
# @click.option('--format', help='Format of the returning project information. json or dataframe', required=True,
#               default='json')
# def info(project_id: str or int, format: str):
#     auth_api.is_user_logged_in()
#     proj = project_api.info(project_id)
#     if proj:
#         if format == 'json':
#             click.echo(proj)
#             return proj
#         elif format == 'dataframe':
#             proj = helper.json_to_dataframe(proj, single_entry=True)
#             click.echo(proj.to_string())
#             return proj
#         else:
#             click.echo(f'Format {format} not available. Return json.')
#             click.echo(proj)
#             return proj
#     else:
#         click.echo("Could not retrieve project info.")
#
#
# @workflow.command('login')
# @click.option('--email', default='test_user@uni-hamburg.de')
# @click.option('--password', default='easm!PLUX3tren3whoh')
# def login(email: str, password: str):
#     r = auth_api.login(email, password)
#     if not r:
#         click.echo('Login failed.')
#     else:
#         click.echo('Login successful.')
#
#
# @workflow.command('logout')
# def logout():
#     r = auth_api.logout()
#     if not r:
#         click.echo('Logout failed.')
#     else:
#
#         click.echo('Logout successful.')
#
#
# @workflow.command('create')
# @click.option('--name', help='Name of the new project.', default='CLI Test Project', required=True)
# @click.option('--description', help='Description of the new project.', default='', required=True)
# def create(name: str, description: str):
#     auth_api.is_user_logged_in()
#     proj_id = project_api.create(name, description)
#     if proj_id:
#         click.echo(f'Created project with id {proj_id}')
#         return proj_id
#     else:
#         click.echo('Creating new project failed.')
#
#
# @workflow.command('delete')
# @click.option('--project_id', help='Id of the project to be deleted.', required=True)
# def remove(project_id: str or int):
#     auth_api.is_user_logged_in()
#     r = project_api.remove(project_id)
#     if r:
#         click.echo('Project deleted successfully.')
#     else:
#         click.echo('Project deletion failed.')
#
#
# @workflow.command('list')
# @click.option('--format', help='Format of the projects list. json or dataframe', required=True, default='json')
# @click.option('--display', help='Display results?', required=True, default=True)
# def list(format: str, display: bool):
#     auth_api.is_user_logged_in()
#     r = project_api.list_projects()
#     if r:
#         if format == 'json':
#             if display:
#                 click.echo(r)
#             return r
#         elif format == 'dataframe':
#             df = helper.json_to_dataframe(r)
#             if display:
#                 click.echo(df.to_string())
#             return df
#         else:
#             if display:
#                 click.echo(f'Format {format} not available. Returning json.')
#             return r
#     else:
#         click.echo('Listing projects failed.')
#
#
# @workflow.command('list_tokens')
# @click.option('--project_id', help='ID of the project.', required=True)
# @click.option('--format', help='Format of the projects list. json or dataframe', required=True, default='json')
# @click.option('--display', help='Display results?', required=True, default=True)
# def list_tokens(project_id: str or int, format: str, display: bool):
#     auth_api.is_user_logged_in()
#     r = project_api.list_tokens(project_id)
#     if r:
#         if format == 'json':
#             if display:
#                 click.echo(r)
#             return r
#         elif format == 'dataframe':
#             df = helper.json_to_dataframe(r)
#             if display:
#                 click.echo(df.to_string())
#             return df
#         else:
#             if display:
#                 click.echo(f'Format {format} not available. Returning json.')
#             return r
#     else:
#         click.echo('Listing tokens failed.')
#
#
# @workflow.command('create_token')
# @click.option('--project_id', help='Id of the project to invite for.', required=True)
# def create_token(project_id: str or int):
#     token = project_api.create_token(project_id)["token"]
#     if token:
#         click.echo(f'You can share the following token: {token}.')
#         return token
#     else:
#         click.echo('Creating invitation token failed.')
#
#
# @workflow.command('remove_token')
# @click.option('--token_id', help='Token of the participant.', required=True)
# def remove_token(token_id: str or int):
#     r = project_api.remove_token(token_id)
#     if r:
#         click.echo('Token removed successfully.')
#     else:
#         click.echo('Removing token failed.')
#
#
# @workflow.command('join')
# @click.option('--token', help='Token to join the project.', required=True)
# def join(token: str):
#     click.echo(f'Join project with token {token}.')


if __name__ == '__main__':
    test()
