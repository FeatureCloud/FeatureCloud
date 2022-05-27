import os
import click
import tqdm

from FeatureCloud.api.imp.app import commands
from FeatureCloud.api.imp.exceptions import FCException


@click.group("app")
def app() -> None:
    """app related commands"""


@app.command('new')
@click.argument('name', type=click.Path(), nargs=1)
@click.argument('directory', type=click.Path(), nargs=1, required=False)
@click.option('--template-name', help='You can specify other template')
def new(name: click.Path, directory: click.Path, template_name: str):
    try:
        path = commands.new(**{k: v for k, v in locals().items() if v})
        click.echo(f'Path to your app: {os.path.abspath(path)}')
        click.echo('Enjoy!')
    except FCException as e:
        click.echo(f'Error: {e}')


@app.command('build')
@click.argument('path', type=click.Path(), default=".", required=False)
@click.argument('image_name', type=str, default='', required=False)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
@click.argument('rm', type=bool, default=True, nargs=1, required=False)
def build(path: click.Path, image_name: str, tag: str, rm: bool):
    try:
        result = commands.build(**{k: v for k, v in locals().items() if v})
        for _ in tqdm.tqdm(result, desc=f"Building {image_name}:{tag} ..."):
            pass
    except FCException as e:
        click.echo(f'Error: {e}')


@app.command('download')
@click.argument('name', type=str, default=None, nargs=1, required=True)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
def download(name: str, tag: str):
    try:
        result = commands.download(**{k: v for k, v in locals().items() if v})
        for _ in tqdm.tqdm(result, desc=f"Downloading {name}:{tag} ..."):
            pass
    except FCException as e:
        click.echo(f'Error: {e}')


@app.command('publish')
@click.argument('name', type=str, default=None, nargs=1, required=True)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
def publish(name: str, tag: str):
    try:
        result = commands.publish(**{k: v for k, v in locals().items() if v})
        for _ in tqdm.tqdm(result, desc=f"Uploading {name}:{tag} ..."):
            pass
    except FCException as e:
        if str(e).find("authentication required") > -1:
            click.echo(f'Image cannot be pushed. A docker login is necessary to featurecloud.ai with user credentials or the app is inexistent in Featurecloud App Store. In this case please create an app in App Store with the specified image name.')
        click.echo(f'Error: {e}')


@app.command('remove')
@click.argument('name', type=str, default=None, nargs=1, required=True)
def remove(name: str):
    try:
        commands.remove(**{k: v for k, v in locals().items() if v})
        click.echo(f'Image {name} removed')
    except FCException as e:
        click.echo(f'Error: {e}')
