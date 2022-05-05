import click
from FeatureCloud.api.imp.app import commands


@click.group("app")
def app() -> None:
    """app related commands"""


@app.command('new')
@click.argument('name', type=click.Path(), nargs=1)
@click.argument('directory', type=click.Path(), nargs=1, required=False)
@click.option('--template-name', help='You can specify other template')
def new(name: click.Path, directory: click.Path, template_name: str):
    _, msg = commands.new(**{k: v for k, v in locals().items() if v})
    click.echo(msg)


@app.command('build')
@click.argument('path', type=click.Path(), default=".", required=False)
@click.argument('image_name', type=str, default='', required=False)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
@click.argument('rm', type=bool, default=False, nargs=1, required=False)
def build(path: click.Path, image_name: str, tag: str, rm: bool):
    _, msg = commands.build(**{k: v for k, v in locals().items() if v})
    click.echo(msg)


@app.command('download')
@click.argument('name', type=str, default=None, nargs=1, required=False)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
def download(name: str, tag: str):
    _, msg = commands.download(**{k: v for k, v in locals().items() if v})
    click.echo(msg)


@app.command('publish')
@click.argument('name', type=str, default=None, nargs=1, required=False)
@click.argument('tag', type=str, default="latest", nargs=1, required=False)
def publish(name: str, tag: str):
    _, msg = commands.publish(**{k: v for k, v in locals().items() if v})
    click.echo(msg)


@app.command('remove')
@click.argument('name', type=str, default=None, nargs=1, required=False)
def remove(name: str):
    _, msg = commands.remove(**{k: v for k, v in locals().items() if v})
    click.echo(msg)
