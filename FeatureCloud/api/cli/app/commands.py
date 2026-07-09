import os
import click
import tqdm

from FeatureCloud.api.imp.app import commands
from FeatureCloud.api.imp.exceptions import FCException


@click.group("app")
def app() -> None:
    """app related commands"""


# @TODO Create a list available templates function

@app.command('new')
@click.argument('name', type=click.Path(), nargs=1)
@click.argument('directory', type=click.Path(), nargs=1, required=False)
@click.option('--template-name',
              help='You can specify a template from the available ones: app-blank, app-dice, app-round. '
                   'If not provided, an empty project will be created using the app-blank template.')
def new(name: click.Path, directory: click.Path, template_name: str):
    """
    Create new app

    NAME is the app name. Because of Docker naming restrictions, it should be in lowercase.

    DIRECTORY is the directory where your app will be created (in a subdirectory NAME)

    Example: featurecloud app new my-new-app . --template-name=app-blank

    """
    try:
        arguments = locals().items()
        for key, value in arguments:
            if key == 'name':
                value_lowercase = value.lower()
                if value != value_lowercase:
                    click.echo("Uppercase letters are not allowed in app name. The new app name is: " + value_lowercase)

        path = commands.new(**{k: v for k, v in arguments if v})
        click.echo(f'Path to your app: {os.path.abspath(path)}')
        click.echo('Enjoy!')
    except FCException as e:
        click.echo(f'Error: {e}')


@app.command('build')
@click.argument('path', type=click.Path(), default=".", required=False)
@click.argument('image_name', type=str, default='', required=False)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
@click.argument('rm', type=bool, default=True, nargs=1, required=False)
@click.pass_context
def build(ctx: click.Context, path: click.Path, image_name: str, tag: str, rm: bool):
    """

    Build app

    PATH is the location of your app

    IMAGE_NAME is the Docker image name. Because of Docker naming restrictions, it should be in lowercase.

    TAG the Docker tag for the version to be built. Default: 'latest'.

    RM remove intermediary containers.

    Example: featurecloud app build ./my-new-app my-new-app first_version True
    """
    profile = "featurecloud"
    if ctx.obj:
        profile = ctx.obj.get("profile", "featurecloud")
    try:
        arguments = locals().items()
        for key, value in arguments:
            if key == 'image_name':
                value_lowercase = value.lower()
                if value != value_lowercase:
                    click.echo(
                        "Uppercase letters are not allowed in image name. The new image name is: " + value_lowercase)
        click.echo(f'Building {image_name}:{tag} ...')
        build_log_generator = commands.build(
            **{k: v for k, v in arguments if v and k not in ('ctx', 'profile')},
            profile=profile,
        )
        # Iterate over the response
        for output in build_log_generator:  
            if 'stream' in output:
                stream_output = output['stream'].strip()
                if 'Step' in stream_output:
                    click.echo(stream_output)
        click.echo(f'Image {image_name}:{tag} built successfully')
        registry_repo = f"{commands.fc_repo_name(image_name.lower(), profile)}:{tag}"
        local_repo = f"{image_name.lower()}:{tag}"
        if registry_repo != local_repo:
            click.echo(f'Also tagged as {registry_repo}')
    except FCException as e:
        click.echo(f'Error: {e}')      


@app.command('download')
@click.argument('name', type=str, default=None, nargs=1, required=True)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
@click.pass_context
def download(ctx: click.Context, name: str, tag: str):
    """
    Download an image from FeatureCloud repository

    NAME is the image name

    TAG is the image versioning tag. Default: 'latest'.

    Example: featurecloud app download my_app:latest
    """
    profile = "featurecloud"
    if ctx.obj:
        profile = ctx.obj.get("profile", "featurecloud")
    try:
        result = commands.download(name, tag, profile)
        for _ in tqdm.tqdm(result, desc=f"Downloading {name}:{tag} ..."):
            pass
    except FCException as e:
        click.echo(f'Error: {e}')


@app.command('publish')
@click.argument('name', type=str, default=None, nargs=1, required=True)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
@click.pass_context
def publish(ctx: click.Context, name: str, tag: str):
    """
    Publish an app in FeatureCloud repository

    NAME is the image name

    TAG is the image versioning tag. Default: 'latest'.

    Example: featurecloud app publish my-app:latest

    The app should be created and the image name set in the AI Store prior publishing

    """
    profile = "featurecloud"
    if ctx.obj:
        profile = ctx.obj.get("profile", "featurecloud")
    registry_host = (
        "fc.cvdlink-project.eu" if profile == "cvdlink" else "featurecloud.ai"
    )
    try:
        result = commands.publish(name, tag, profile)
        for _ in tqdm.tqdm(result, desc=f"Uploading {name}:{tag} ..."):
            pass
    except FCException as e:
        if str(e).find("authentication required") > -1:
            click.echo(
                f"Image cannot be pushed. Run `docker login {registry_host}` with credentials that can push "
                f"this repository, or ensure the app exists in the platform app store with image name `{name}`."
            )
        click.echo(f'Error: {e}')


@app.command('remove')
@click.argument('name', type=str, default=None, nargs=1, required=True)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
@click.pass_context
def remove(ctx: click.Context, name: str, tag: str):
    """
    Delete app image(s) from the local repository. This command will not delete the app from FeatureCloud AI Store.

    NAME is the image name to be deleted

    TAG is the image versioning tag. If set to 'all', all versions will be deleted. Default: 'latest'.

    Example: featurecloud app remove my-app all
    """
    profile = "featurecloud"
    if ctx.obj:
        profile = ctx.obj.get("profile", "featurecloud")
    try:
        result = commands.remove(name, tag, profile)
        if len(result) == 0:
            click.echo(f'No image found')
        else:
            click.echo(f'Removed image(s): {",".join(result)}')
    except FCException as e:
        click.echo(f'Error: {e}')


@app.command('plot-states')
@click.argument('path', type=click.Path(), default=".", required=False)
@click.option('--package', default=".", help='package/s which include/s the states')
@click.option('--states', default='main', help='python files containing the states seperated by comma')
@click.option('--plot_name', default="state_diagram", help='name of the plotted diagram file')
def plot_diagram(path: str, package: str, states: str, plot_name: str):
    """
    Plot and store the state diagram of the app in the app directory

    Path is the path to directory containing the app

    Package is the relative path of the subpackage containing the states

    States is a comma seperated list of .py files including the states

    Plot_name is the name of the plotted diagram file

    Example: featurecloud app plot-states /home/my-app mystates --states states.py --plot_name myplot
    """
    try:
        commands.plot_state_diagram(**{k: v for k, v in locals().items() if v})
    except FCException as e:
        click.echo(f'Error: {e}')
