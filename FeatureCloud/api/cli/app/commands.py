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
    _, msg = commands.new(**{k: v for k , v in locals().items() if v})
    click.echo(msg)
